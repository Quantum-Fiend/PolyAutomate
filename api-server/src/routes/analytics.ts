import { Router, Request, Response } from 'express';
import { Pool } from 'pg';
import { authenticateToken } from '../middleware/auth';

const router = Router();

const pool = new Pool({
    host: process.env.DB_HOST || 'localhost',
    port: parseInt(process.env.DB_PORT || '5432'),
    database: process.env.DB_NAME || 'omnitasker',
    user: process.env.DB_USER || 'omnitasker',
    password: process.env.DB_PASSWORD || 'omnitasker_secure_pass'
});

// Get execution statistics
router.get('/executions', authenticateToken, async (req: Request, res: Response) => {
    try {
        const days = parseInt(req.query.days as string) || 7;

        const result = await pool.query(
            `SELECT 
        DATE(started_at) as date,
        COUNT(*) as total,
        COUNT(CASE WHEN status = 'success' THEN 1 END) as successful,
        COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed,
        AVG(duration_ms) as avg_duration
       FROM task_executions
       WHERE started_at >= CURRENT_DATE - INTERVAL '${days} days'
       GROUP BY DATE(started_at)
       ORDER BY date DESC`
        );

        res.json(result.rows);
    } catch (error) {
        res.status(500).json({ error: 'Failed to fetch execution statistics' });
    }
});

// Get task success rates
router.get('/success-rate', authenticateToken, async (req: Request, res: Response) => {
    try {
        const result = await pool.query(
            `SELECT * FROM task_execution_stats ORDER BY total_executions DESC`
        );

        res.json(result.rows);
    } catch (error) {
        res.status(500).json({ error: 'Failed to fetch success rates' });
    }
});

// Get AI results
router.get('/ai-results', authenticateToken, async (req: Request, res: Response) => {
    try {
        const limit = parseInt(req.query.limit as string) || 50;

        const result = await pool.query(
            `SELECT * FROM ai_results 
       ORDER BY created_at DESC 
       LIMIT $1`,
            [limit]
        );

        res.json(result.rows);
    } catch (error) {
        res.status(500).json({ error: 'Failed to fetch AI results' });
    }
});

// Get system overview
router.get('/overview', authenticateToken, async (req: Request, res: Response) => {
    try {
        const [tasksResult, executionsResult, pluginsResult] = await Promise.all([
            pool.query('SELECT COUNT(*) as total, COUNT(CASE WHEN is_enabled THEN 1 END) as enabled FROM tasks'),
            pool.query(`SELECT 
        COUNT(*) as total,
        COUNT(CASE WHEN status = 'success' THEN 1 END) as successful,
        COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed,
        COUNT(CASE WHEN status = 'running' THEN 1 END) as running
       FROM task_executions
       WHERE started_at >= CURRENT_DATE - INTERVAL '24 hours'`),
            pool.query('SELECT COUNT(*) as total, COUNT(CASE WHEN is_enabled THEN 1 END) as enabled FROM plugins')
        ]);

        res.json({
            tasks: tasksResult.rows[0],
            executions_24h: executionsResult.rows[0],
            plugins: pluginsResult.rows[0]
        });
    } catch (error) {
        res.status(500).json({ error: 'Failed to fetch overview' });
    }
});

export default router;
