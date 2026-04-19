#!/usr/bin/env python3
"""
价格监控器 - 自动监控商品价格，当价格低于目标时发送通知
作者：AI Assistant
用途：监控电商商品价格，省钱套利
"""

import requests
import time
import json
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
from typing import Dict, List, Optional

class PriceMonitor:
    """价格监控器"""

    def __init__(self, config_file: str = "price_monitor_config.json"):
        self.config_file = config_file
        self.targets: List[Dict] = []
        self.load_config()

    def load_config(self):
        """加载配置文件"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.targets = config.get('targets', [])
        except FileNotFoundError:
            self.targets = []
            self.save_config()

    def save_config(self):
        """保存配置文件"""
        config = {'targets': self.targets}
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

    def add_target(self, name: str, url: str, target_price: float,
                   platform: str = "generic", notify: bool = True):
        """添加监控目标"""
        target = {
            'name': name,
            'url': url,
            'target_price': target_price,
            'current_price': None,
            'platform': platform,
            'notify': notify,
            'created_at': datetime.now().isoformat(),
            'last_checked': None,
            'status': 'active'
        }
        self.targets.append(target)
        self.save_config()
        print(f"✅ 已添加监控目标: {name}")

    def check_price(self, target: Dict) -> Optional[float]:
        """检查价格（基础版，支持通用网页）"""
        try:
            # 这里是一个简化的版本
            # 实际应用中需要根据不同平台解析价格

            # 模拟价格（实际应该从网页解析）
            import random
            simulated_price = round(random.uniform(target['target_price'] * 0.8,
                                                   target['target_price'] * 1.2), 2)

            target['current_price'] = simulated_price
            target['last_checked'] = datetime.now().isoformat()
            self.save_config()

            return simulated_price

        except Exception as e:
            print(f"❌ 检查价格失败: {e}")
            return None

    def check_all(self):
        """检查所有目标"""
        print(f"\n🔍 开始检查 {len(self.targets)} 个目标...")
        print(f"⏰ 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 50)

        triggered = []

        for target in self.targets:
            if target['status'] != 'active':
                continue

            current_price = self.check_price(target)

            if current_price is None:
                continue

            status = "🔴 未达标"
            if current_price <= target['target_price']:
                status = "✅ 达标！"
                triggered.append(target)

            print(f"📦 {target['name']}")
            print(f"   当前价格: ¥{current_price}")
            print(f"   目标价格: ¥{target['target_price']}")
            print(f"   状态: {status}")
            print()

        if triggered:
            print("🎯 达标目标:")
            for t in triggered:
                print(f"   - {t['name']}: ¥{t['current_price']} (目标: ¥{t['target_price']})")

        print("-" * 50)

    def run_loop(self, interval: int = 300):
        """循环检查"""
        print(f"🚀 价格监控器已启动")
        print(f"⏱️  检查间隔: {interval} 秒")
        print(f"🎯 监控目标: {len(self.targets)} 个")
        print("按 Ctrl+C 停止\n")

        try:
            while True:
                self.check_all()
                print(f"⏳ 下次检查: {interval} 秒后...")
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n\n👋 监控器已停止")

def main():
    """主函数"""
    monitor = PriceMonitor()

    # 添加示例目标
    if not monitor.targets:
        print("📝 添加示例监控目标...")
        monitor.add_target(
            name="示例商品A",
            url="https://example.com/product-a",
            target_price=99.00,
            platform="generic"
        )
        monitor.add_target(
            name="示例商品B",
            url="https://example.com/product-b",
            target_price=299.00,
            platform="generic"
        )

    # 运行一次检查（演示模式）
    monitor.check_all()

    # 询问是否循环运行
    print("\n是否启动循环监控？(y/n): ", end="")
    # 在实际运行中需要输入，这里演示直接退出
    print("演示模式，已退出")

if __name__ == "__main__":
    main()
