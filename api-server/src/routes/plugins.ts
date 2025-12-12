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

// Get all plugins
router.get('/', authenticateToken, async (req: Request, res: Response) => {
    try {
        const result = await pool.query(
            'SELECT * FROM plugins ORDER BY name'
        );
        res.json(result.rows);
    } catch (error) {
        res.status(500).json({ error: 'Failed to fetch plugins' });
    }
});

// Get single plugin
router.get('/:id', authenticateToken, async (req: Request, res: Response) => {
    try {
        const { id } = req.params;
        const result = await pool.query(
            'SELECT * FROM plugins WHERE id = $1',
            [id]
        );

        if (result.rows.length === 0) {
            return res.status(404).json({ error: 'Plugin not found' });
        }

        res.json(result.rows[0]);
    } catch (error) {
        res.status(500).json({ error: 'Failed to fetch plugin' });
    }
});

// Register new plugin
router.post('/', authenticateToken, async (req: Request, res: Response) => {
    try {
        const { name, description, plugin_type, version, author, file_path, config } = req.body;

        const result = await pool.query(
            `INSERT INTO plugins (name, description, plugin_type, version, author, file_path, config)
       VALUES ($1, $2, $3, $4, $5, $6, $7)
       RETURNING *`,
            [name, description, plugin_type, version, author, file_path, config || {}]
        );

        res.status(201).json(result.rows[0]);
    } catch (error) {
        res.status(500).json({ error: 'Failed to register plugin' });
    }
});

// Update plugin
router.put('/:id', authenticateToken, async (req: Request, res: Response) => {
    try {
        const { id } = req.params;
        const { name, description, is_enabled, config } = req.body;

        const result = await pool.query(
            `UPDATE plugins 
       SET name = COALESCE($1, name),
           description = COALESCE($2, description),
           is_enabled = COALESCE($3, is_enabled),
           config = COALESCE($4, config),
           updated_at = CURRENT_TIMESTAMP
       WHERE id = $5
       RETURNING *`,
            [name, description, is_enabled, config, id]
        );

        if (result.rows.length === 0) {
            return res.status(404).json({ error: 'Plugin not found' });
        }

        res.json(result.rows[0]);
    } catch (error) {
        res.status(500).json({ error: 'Failed to update plugin' });
    }
});

// Delete plugin
router.delete('/:id', authenticateToken, async (req: Request, res: Response) => {
    try {
        const { id } = req.params;

        const result = await pool.query(
            'DELETE FROM plugins WHERE id = $1 RETURNING id',
            [id]
        );

        if (result.rows.length === 0) {
            return res.status(404).json({ error: 'Plugin not found' });
        }

        res.json({ message: 'Plugin deleted successfully' });
    } catch (error) {
        res.status(500).json({ error: 'Failed to delete plugin' });
    }
});

export default router;
