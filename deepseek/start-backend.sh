#!/bin/bash
cd /home/group.s7/m.goloshchanov/IdeaProjects/SkillsTest/deepseek/backend
rm -f db/warehouse.db
exec /usr/bin/python3.10 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
