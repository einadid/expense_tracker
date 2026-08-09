#!/bin/bash
find / -name "uvicorn" 2>/dev/null | head -5
/opt/render/project/python/bin/python -m uvicorn main:app --host 0.0.0.0 --port $PORT