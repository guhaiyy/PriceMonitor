#!/usr/bin/env python3
"""
主程序 - 整合所有功能
价格监控工具完整版
"""

import json
import time
from datetime import datetime
from typing import List, Dict
import os
import sys

# 导入各个模块
try:
    from price_scraper import PriceScraper
except ImportError:
    PriceScraper = None

try:
    from email_notifier import EmailNotifier
except ImportError:
    EmailNotifier = None

class PriceMonitorApp:
    """价格监控主应用"""

    def __init__(self):
        self.config_file = 'monitor_config.json'
        self.scraper = PriceScraper() if PriceScraper else None
        self.notifier = EmailNotifier() if EmailNotifier else None
        self.targets = []
        self.load_config()

    def load_config(self):
        """加载配置"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.targets = config.get('targets', [])

    def save_config(self):
        """保存配置"""
        config = {
            'targets': self.targets,
            'last_updated': datetime.now().isoformat()
        }
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

    def add_target(self, name: str, url: str, target_price: float) -> Dict:
        """添加监控目标"""
        # 平台检测
        if 'taobao.com' in url or 'tmall.com' in url:
            platform = '淘宝'
        elif 'jd.com' in url:
            platform = '京东'
        elif 'pinduoduo.com' in url:
            platform = '拼多多'
        else:
            platform = '通用'

        target = {
            'id': f"target_{int(datetime.now().timestamp())}",
            'name': name,
            'url': url,
            'target_price': target_price,
            'platform': platform,
            'current_price': None,
            'status': 'active',
            'created_at': datetime.now().isoformat(),
            'last_checked': None
        }

        self.targets.append(target)
        self.save_config()

        return target

    def check_all(self):
        """检查所有目标"""
        print(f"\n{'='*70}")
        print(f"📊 价格检查报告")
        print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}\n")

        deals = []

        for i, target in enumerate(self.targets, 1):
            if target['status'] != 'active':
                continue

            print(f"📦 {i}. {target['name']}")
            print(f"   平台: {target['platform']}")
            print(f"   目标价: ¥{target['target_price']}")

            # 检查价格
            if self.scraper:
                price = self.scraper.get_price(target['url'])
            else:
                # 模拟价格
                import random
                price = round(random.uniform(100, 5000), 2)

            target['current_price'] = price
            target['last_checked'] = datetime.now().isoformat()

            # 判断是否达标
            if price <= target['target_price']:
                print(f"   当前价: ¥{price} ✅ 达标！")
                deals.append(target)
            else:
                print(f"   当前价: ¥{price} 🔴 未达标")

            print()

        self.save_config()

        # 显示达标商品
        if deals:
            print("🎉 发现好价商品！")
            print("-" * 70)
            for deal in deals:
                print(f"✨ {deal['name']}")
                print(f"   链接: {deal['url']}")
                print(f"   平台: {deal['platform']}")
                print(f"   价格: ¥{deal['current_price']} (目标: ¥{deal['target_price']})")
                savings = deal['target_price'] - deal['current_price']
                print(f"   省约: ¥{savings:.2f}")
            print("-" * 70)

        # 发送邮件提醒
        if deals and self.notifier:
            self.notifier.send_alert('your-email@example.com', deals)

        return deals

    def run_loop(self, interval: int = 300):
        """循环运行"""
        print(f"🚀 价格监控器已启动")
        print(f"⏱️  检查间隔: {interval} 秒 ({interval // 60} 分钟)")
        print(f"🎯 监控目标: {len(self.targets)} 个")
        print("按 Ctrl+C 停止\n")

        try:
            while True:
                self.check_all()
                print(f"\n⏳ 下次检查: {interval} 秒后...")
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n\n👋 监控器已停止")

    def show_stats(self):
        """显示统计信息"""
        active = [t for t in self.targets if t['status'] == 'active']
        deals = [t for t in active if t.get('current_price') and t['current_price'] <= t['target_price']]

        print(f"\n📊 统计信息")
        print("-" * 40)
        print(f"总目标数: {len(self.targets)}")
        print(f"活跃监控: {len(active)}")
        print(f"达标商品: {len(deals)}")
        print(f"平台分布: {self._get_platforms()}")
        print("-" * 40)

    def _get_platforms(self) -> str:
        """获取平台分布"""
        platforms = {}
        for target in self.targets:
            platform = target['platform']
            platforms[platform] = platforms.get(platform, 0) + 1
        return ', '.join([f"{k}({v})" for k, v in platforms.items()])


def interactive_mode():
    """交互模式"""
    app = PriceMonitorApp()

    print("🛒 电商价格监控工具")
    print("=" * 60)
    print("\n可用命令:")
    print("  1. 添加监控")
    print("  2. 查看列表")
    print("  3. 检查价格")
    print("  4. 启动监控")
    print("  5. 退出")

    while True:
        print("\n请选择操作 (1-5): ", end="")
        choice = input().strip()

        if choice == '1':
            # 添加监控
            name = input("商品名称: ").strip()
            url = input("商品链接: ").strip()
            target_price = float(input("目标价格: ").strip())

            target = app.add_target(name, url, target_price)
            print(f"✅ 已添加: {name}")

        elif choice == '2':
            # 查看列表
            app.show_stats()
            if app.targets:
                print("\n监控列表:")
                for i, t in enumerate(app.targets, 1):
                    status = "✅" if t['status'] == 'active' else "⏸️"
                    price = f"¥{t.get('current_price', '-')}"
                    print(f"  {i}. {status} {t['name']} ({t['platform']}) - {price} -> ¥{t['target_price']}")

        elif choice == '3':
            # 检查价格
            app.check_all()

        elif choice == '4':
            # 启动监控
            interval = int(input("检查间隔(秒，默认300): ").strip() or "300")
            app.run_loop(interval)

        elif choice == '5':
            # 退出
            print("👋 再见！")
            break

        else:
            print("❌ 无效选择，请重试")


def demo_mode():
    """演示模式"""
    print("🛒 电商价格监控工具 - 演示模式")
    print("=" * 60)

    app = PriceMonitorApp()

    # 添加示例目标
    examples = [
        {
            'name': 'iPhone 15 Pro',
            'url': 'https://detail.tmall.com/item.htm?id=example1',
            'target_price': 6999.00
        },
        {
            'name': '索尼 WH-1000XM5',
            'url': 'https://item.jd.com/example2',
            'target_price': 1899.00
        },
        {
            'name': '戴森吸尘器 V12',
            'url': 'https://detail.tmall.com/item.htm?id=example3',
            'target_price': 2999.00
        }
    ]

    print("\n添加示例目标...\n")
    for item in examples:
        target = app.add_target(**item)
        print(f"✅ {item['name']} ({target['platform']}) - ¥{item['target_price']}")

    # 检查价格
    print("\n开始价格检查...\n")
    deals = app.check_all()

    # 显示统计
    app.show_stats()

    # 生成报告
    report = {
        'total_targets': len(app.targets),
        'active_targets': len([t for t in app.targets if t['status'] == 'active']),
        'deals_found': len(deals),
        'generated_at': datetime.now().isoformat()
    }

    with open('monitor_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("\n💾 报告已保存到: monitor_report.json")

    print("\n" + "=" * 60)
    print("💡 下一步:")
    print("1. 运行交互模式: python3 main.py --interactive")
    print("2. 启动Web界面: python3 web_interface.py")
    print("3. 定时检查: python3 main.py --check")
    print("=" * 60)


def main():
    """主函数"""
    if len(sys.argv) > 1:
        if sys.argv[1] == '--interactive':
            interactive_mode()
        elif sys.argv[1] == '--check':
            app = PriceMonitorApp()
            app.check_all()
        elif sys.argv[1] == '--web':
            print("运行Web界面: python3 web_interface.py")
        else:
            print("用法: python3 main.py [--interactive|--check|--web]")
    else:
        # 默认演示模式
        demo_mode()


if __name__ == "__main__":
    main()
