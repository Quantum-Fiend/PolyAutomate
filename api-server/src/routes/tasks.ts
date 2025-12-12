import { Router, Request, Response } from 'express';
import { Pool } from 'pg';
import { authenticateToken } from '../middleware/auth';

const router = Router();

// Database connection
const pool = new Pool({
    host: process.env.DB_HOST || 'localhost',
    port: parseInt(process.env.DB_PORT || '5432'),
    database: process.env.DB_NAME || 'omnitasker',
    user: process.env.DB_USER || 'omnitasker',
    password: process.env.DB_PASSWORD || 'omnitasker_secure_pass'
});

// Get all tasks
router.get('/', authenticateToken, async (req: Request, res: Response) => {
    try {
        const result = await pool.query(
            'SELECT * FROM tasks WHERE user_id = $1 ORDER BY created_at DESC',
            [req.user?.userId]
        );
        res.json(result.rows);
    } catch (error) {
        res.status(500).json({ error: 'Failed to fetch tasks' });
    }
});

// Get single task
router.get('/:id', authenticateToken, async (req: Request, res: Response) => {
    try {
        const { id } = req.params;
        const result = await pool.query(
            'SELECT * FROM tasks WHERE id = $1 AND user_id = $2',
            [id, req.user?.userId]
        );

        if (result.rows.length === 0) {
            return res.status(404).json({ error: 'Task not found' });
        }

        res.json(result.rows[0]);
    } catch (error) {
        res.status(500).json({ error: 'Failed to fetch task' });
    }
});

// Create new task
router.post('/', authenticateToken, async (req: Request, res: Response) => {
    try {
        const { name, description, script_type, script_content, script_path, metadata } = req.body;

        const result = await pool.query(
            `INSERT INTO tasks (user_id, name, description, script_type, script_content, script_path, metadata)
       VALUES ($1, $2, $3, $4, $5, $6, $7)
       RETURNING *`,
            [req.user?.userId, name, description, script_type, script_content, script_path, metadata || {}]
        );

        res.status(201).json(result.rows[0]);
    } catch (error) {
        res.status(500).json({ error: 'Failed to create task' });
    }
});

// Update task
router.put('/:id', authenticateToken, async (req: Request, res: Response) => {
    try {
        const { id } = req.params;
        const { name, description, script_type, script_content, script_path, is_enabled, metadata } = req.body;

        const result = await pool.query(
            `UPDATE tasks 
       SET name = COALESCE($1, name),
           description = COALESCE($2, description),
           script_type = COALESCE($3, script_type),
           script_content = COALESCE($4, script_content),
           script_path = COALESCE($5, script_path),
           is_enabled = COALESCE($6, is_enabled),
           metadata = COALESCE($7, metadata),
           updated_at = CURRENT_TIMESTAMP
       WHERE id = $8 AND user_id = $9
       RETURNING *`,
            [name, description, script_type, script_content, script_path, is_enabled, metadata, id, req.user?.userId]
        );

        if (result.rows.length === 0) {
            return res.status(404).json({ error: 'Task not found' });
        }

        res.json(result.rows[0]);
    } catch (error) {
        res.status(500).json({ error: 'Failed to update task' });
    }
});

// Delete task
router.delete('/:id', authenticateToken, async (req: Request, res: Response) => {
    try {
        const { id } = req.params;

        const result = await pool.query(
            'DELETE FROM tasks WHERE id = $1 AND user_id = $2 RETURNING id',
            [id, req.user?.userId]
        );

        if (result.rows.length === 0) {
            return res.status(404).json({ error: 'Task not found' });
        }

        res.json({ message: 'Task deleted successfully' });
    } catch (error) {
        res.status(500).json({ error: 'Failed to delete task' });
    }
});

// Execute task
router.post('/:id/execute', authenticateToken, async (req: Request, res: Response) => {
    try {
        const { id } = req.params;

        // Check if task exists
        const taskResult = await pool.query(
            'SELECT * FROM tasks WHERE id = $1 AND user_id = $2',
            [id, req.user?.userId]
        );

        if (taskResult.rows.length === 0) {
            return res.status(404).json({ error: 'Task not found' });
        }

        // Create execution record
        const executionResult = await pool.query(
            `INSERT INTO task_executions (task_id, status, triggered_by)
       VALUES ($1, 'pending', 'api')
       RETURNING *`,
            [id]
        );

        // In a real implementation, this would trigger the Python automation engine
        // For now, we just return the execution ID
        res.json({
            message: 'Task execution initiated',
            execution: executionResult.rows[0]
        });
    } catch (error) {
        res.status(500).json({ error: 'Failed to execute task' });
    }
});

// Get task executions
router.get('/:id/executions', authenticateToken, async (req: Request, res: Response) => {
    try {
        const { id } = req.params;
        const limit = parseInt(req.query.limit as string) || 50;

        const result = await pool.query(
            `SELECT te.* FROM task_executions te
       JOIN tasks t ON te.task_id = t.id
       WHERE t.id = $1 AND t.user_id = $2
       ORDER BY te.started_at DESC
       LIMIT $3`,
            [id, req.user?.userId, limit]
        );

        res.json(result.rows);
    } catch (error) {
        res.status(500).json({ error: 'Failed to fetch executions' });
    }
});

export default router;
