import { Server as SocketIOServer, Socket } from 'socket.io';

export const setupWebSocket = (io: SocketIOServer) => {
    io.on('connection', (socket: Socket) => {
        console.log(`✓ Client connected: ${socket.id}`);

        // Join task execution room
        socket.on('join_execution', (executionId: string) => {
            socket.join(`execution_${executionId}`);
            console.log(`Client ${socket.id} joined execution room: ${executionId}`);
        });

        // Leave task execution room
        socket.on('leave_execution', (executionId: string) => {
            socket.leave(`execution_${executionId}`);
            console.log(`Client ${socket.id} left execution room: ${executionId}`);
        });

        // Handle disconnect
        socket.on('disconnect', () => {
            console.log(`✗ Client disconnected: ${socket.id}`);
        });
    });

    // Helper function to emit execution updates
    const emitExecutionUpdate = (executionId: string, data: any) => {
        io.to(`execution_${executionId}`).emit('execution_update', data);
    };

    // Helper function to emit log updates
    const emitLogUpdate = (executionId: string, log: string) => {
        io.to(`execution_${executionId}`).emit('log_update', { log });
    };

    // Helper function to broadcast system notifications
    const broadcastNotification = (notification: any) => {
        io.emit('notification', notification);
    };

    return {
        emitExecutionUpdate,
        emitLogUpdate,
        broadcastNotification
    };
};
