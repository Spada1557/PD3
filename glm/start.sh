#!/bin/bash
set -e
cd "$(dirname "$0")"

BACKEND_PORT=${1:-$(python3 -c "import socket; s=socket.socket(); s.bind(('',0)); print(s.getsockname()[1]); s.close()")}
FRONTEND_PORT=${2:-$(python3 -c "import socket; s=socket.socket(); s.bind(('',0)); print(s.getsockname()[1]); s.close()")}

echo "============================================="
echo "  Enamelware Accounting System"
echo "============================================="
echo "  Backend:   http://127.0.0.1:$BACKEND_PORT"
echo "  API docs:  http://127.0.0.1:$BACKEND_PORT/docs"
echo "  Frontend:  http://127.0.0.1:$FRONTEND_PORT"
echo "============================================="
echo "  Login: admin@enamelware.ru / admin123"
echo "         manager@enamelware.ru / manager123"
echo "         warehouse@enamelware.ru / warehouse123"
echo "============================================="

# Update vite config
cat > enamelware-frontend/vite.config.js << EOF
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: $FRONTEND_PORT,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:$BACKEND_PORT',
        changeOrigin: true,
      },
      '/uploads': {
        target: 'http://127.0.0.1:$BACKEND_PORT',
        changeOrigin: true,
      },
    },
  },
})
EOF

# Init DB
cd enamelware-backend
rm -f enamelware.db
python3 -c "from enamelware.database import init_db, SessionLocal; from enamelware.seed import seed_database; init_db(); db = SessionLocal(); seed_database(db); db.close(); print('DB OK')"

# Start backend
python3 -m uvicorn enamelware.main:app --host 127.0.0.1 --port $BACKEND_PORT &
BACKEND_PID=$!

# Start frontend
cd ../enamelware-frontend
npx vite --host 127.0.0.1 --port $FRONTEND_PORT &
FRONTEND_PID=$!

# Save PIDs and ports
echo "$BACKEND_PID" > /tmp/ew_backend_pid
echo "$FRONTEND_PID" > /tmp/ew_frontend_pid
echo "$BACKEND_PORT" > /tmp/ew_backend_port
echo "$FRONTEND_PORT" > /tmp/ew_frontend_port

echo ""
echo "PIDs: backend=$BACKEND_PID frontend=$FRONTEND_PID"
echo "To stop: kill $BACKEND_PID $FRONTEND_PID"

wait