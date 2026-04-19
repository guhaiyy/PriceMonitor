#!/usr/bin/env python3
"""
Web界面 - 价格监控工具的Web管理界面
使用Flask创建简单的Web界面
"""

from flask import Flask, render_template_string, request, jsonify, redirect, url_for
import json
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# 数据存储
DATA_FILE = 'monitor_data.json'

# HTML模板
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>价格监控工具</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
        }
        .card {
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        h1 {
            color: #667eea;
            margin-bottom: 10px;
            font-size: 28px;
        }
        .subtitle {
            color: #999;
            margin-bottom: 30px;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }
        .stat-box {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        .stat-number {
            font-size: 32px;
            font-weight: bold;
            color: #667eea;
        }
        .stat-label {
            color: #999;
            font-size: 14px;
            margin-top: 5px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 500;
        }
        input, select {
            width: 100%;
            padding: 12px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            font-size: 16px;
        }
        input:focus, select:focus {
            outline: none;
            border-color: #667eea;
        }
        button {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s;
        }
        button:hover {
            transform: translateY(-2px);
        }
        .monitor-list {
            margin-top: 30px;
        }
        .monitor-item {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .monitor-info {
            flex: 1;
        }
        .monitor-name {
            font-weight: bold;
            color: #333;
        }
        .monitor-price {
            color: #667eea;
            font-size: 18px;
            font-weight: bold;
        }
        .monitor-platform {
            background: #e9ecef;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            color: #666;
        }
        .status-active {
            color: #28a745;
        }
        .status-inactive {
            color: #999;
        }
        .delete-btn {
            background: #dc3545;
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            margin-left: 10px;
        }
        .delete-btn:hover {
            background: #c82333;
        }
        .check-btn {
            background: #28a745;
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            margin-right: 10px;
        }
        .check-btn:hover {
            background: #218838;
        }
        .empty-state {
            text-align: center;
            color: #999;
            padding: 40px;
        }
        .footer {
            text-align: center;
            color: #999;
            font-size: 14px;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <h1>🛒 价格监控工具</h1>
            <p class="subtitle">自动监控商品价格，好价不错过</p>

            <div class="stats">
                <div class="stat-box">
                    <div class="stat-number" id="totalCount">0</div>
                    <div class="stat-label">监控总数</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number" id="activeCount">0</div>
                    <div class="stat-label">活跃监控</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number" id="dealCount">0</div>
                    <div class="stat-label">达标商品</div>
                </div>
            </div>

            <form id="addForm">
                <div class="form-group">
                    <label>商品名称</label>
                    <input type="text" id="name" required placeholder="例如：iPhone 15 Pro">
                </div>
                <div class="form-group">
                    <label>商品链接</label>
                    <input type="url" id="url" required placeholder="https://...">
                </div>
                <div class="form-group">
                    <label>目标价格 (元)</label>
                    <input type="number" id="targetPrice" required placeholder="例如：6999">
                </div>
                <button type="submit">➕ 添加监控</button>
            </form>

            <div class="monitor-list">
                <h3>📋 监控列表</h3>
                <div id="monitorList">
                    <!-- 监控项会动态插入这里 -->
                </div>
            </div>

            <div class="footer">
                <p>最后更新: <span id="lastUpdate">-</span></p>
                <p>价格监控工具 v1.0 | 由 AI 助手创建</p>
            </div>
        </div>
    </div>

    <script>
        // 加载监控列表
        function loadMonitors() {
            fetch('/api/monitors')
                .then(response => response.json())
                .then(data => {
                    updateStats(data);
                    renderMonitors(data);
                    document.getElementById('lastUpdate').textContent = new Date().toLocaleString();
                })
                .catch(error => console.error('Error:', error));
        }

        // 更新统计数据
        function updateStats(monitors) {
            const total = monitors.length;
            const active = monitors.filter(m => m.status === 'active').length;
            const deals = monitors.filter(m => m.current_price <= m.target_price).length;

            document.getElementById('totalCount').textContent = total;
            document.getElementById('activeCount').textContent = active;
            document.getElementById('dealCount').textContent = deals;
        }

        // 渲染监控列表
        function renderMonitors(monitors) {
            const container = document.getElementById('monitorList');

            if (monitors.length === 0) {
                container.innerHTML = '<div class="empty-state">还没有添加任何监控目标</div>';
                return;
            }

            container.innerHTML = monitors.map(m => `
                <div class="monitor-item">
                    <div class="monitor-info">
                        <div class="monitor-name">${escapeHtml(m.name)}</div>
                        <div>
                            <span class="monitor-platform">${escapeHtml(m.platform)}</span>
                            <span class="monitor-price">¥${m.current_price || '-'}</span>
                            <span style="color: #999; font-size: 14px;">目标: ¥${m.target_price}</span>
                        </div>
                    </div>
                    <div>
                        <button class="check-btn" onclick="checkPrice('${m.id}')">🔍 检查</button>
                        <button class="delete-btn" onclick="deleteMonitor('${m.id}')">🗑️</button>
                    </div>
                </div>
            `).join('');
        }

        // 添加监控
        document.getElementById('addForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const data = {
                name: document.getElementById('name').value,
                url: document.getElementById('url').value,
                target_price: parseFloat(document.getElementById('targetPrice').value)
            };

            fetch('/api/monitors', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    document.getElementById('addForm').reset();
                    loadMonitors();
                } else {
                    alert('添加失败: ' + data.error);
                }
            });
        });

        // 删除监控
        function deleteMonitor(id) {
            if (confirm('确定要删除这个监控吗？')) {
                fetch(`/api/monitors/${id}`, {method: 'DELETE'})
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            loadMonitors();
                        }
                    });
            }
        }

        // 检查价格
        function checkPrice(id) {
            fetch(`/api/monitors/${id}/check`, {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert(`当前价格: ¥${data.price}`);
                        loadMonitors();
                    } else {
                        alert('检查失败: ' + data.error);
                    }
                });
        }

        // HTML转义
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        // 页面加载时加载数据
        loadMonitors();

        // 定时刷新（每分钟）
        setInterval(loadMonitors, 60000);
    </script>
</body>
</html>
"""

def load_data():
    """加载数据"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'monitors': []}

def save_data(data):
    """保存数据"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route('/')
def index():
    """首页"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/monitors', methods=['GET'])
def get_monitors():
    """获取监控列表"""
    data = load_data()
    return jsonify(data.get('monitors', []))

@app.route('/api/monitors', methods=['POST'])
def add_monitor():
    """添加监控"""
    data = request.json

    # 简单的平台检测
    url = data.get('url', '')
    if 'taobao.com' in url or 'tmall.com' in url:
        platform = '淘宝'
    elif 'jd.com' in url:
        platform = '京东'
    elif 'pinduoduo.com' in url:
        platform = '拼多多'
    else:
        platform = '通用'

    monitor = {
        'id': f"monitor_{datetime.now().timestamp()}",
        'name': data.get('name'),
        'url': url,
        'target_price': data.get('target_price'),
        'platform': platform,
        'current_price': None,
        'status': 'active',
        'created_at': datetime.now().isoformat(),
        'last_checked': None
    }

    data = load_data()
    data['monitors'].append(monitor)
    save_data(data)

    return jsonify({'success': True, 'monitor': monitor})

@app.route('/api/monitors/<monitor_id>', methods=['DELETE'])
def delete_monitor(monitor_id):
    """删除监控"""
    data = load_data()
    data['monitors'] = [m for m in data['monitors'] if m['id'] != monitor_id]
    save_data(data)
    return jsonify({'success': True})

@app.route('/api/monitors/<monitor_id>/check', methods=['POST'])
def check_price(monitor_id):
    """检查价格"""
    data = load_data()
    monitor = next((m for m in data['monitors'] if m['id'] == monitor_id), None)

    if not monitor:
        return jsonify({'success': False, 'error': 'Monitor not found'})

    # 模拟价格检查（实际应该调用 price_scraper）
    import random
    price = round(random.uniform(100, 5000), 2)

    monitor['current_price'] = price
    monitor['last_checked'] = datetime.now().isoformat()

    save_data(data)

    return jsonify({'success': True, 'price': price})

if __name__ == '__main__':
    print("🌐 价格监控Web界面")
    print("=" * 60)
    print("启动Web服务器...")
    print("访问地址: http://localhost:5000")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=True)
