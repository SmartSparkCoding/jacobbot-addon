#!/usr/bin/env bash
export SLACK_BOT_TOKEN=$(bashio::config 'slack_bot_token')
export SLACK_APP_TOKEN=$(bashio::config 'slack_app_token')

python3 /app/bot.py
