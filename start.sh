#!/bin/bash
export PATH="/opt/render/project/python/bin:$PATH"
uvicorn main:app --host 0.0.0.0 --port $PORT