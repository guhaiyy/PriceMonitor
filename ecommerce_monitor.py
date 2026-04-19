#!/usr/bin/env python3
"""
商品价格监控工具 - 支持淘宝/京东等电商平台
用途：自动监控商品价格，低于目标价时提醒
市场价值：帮助用户省钱、代购套利
"""

import requests
import json
import time
import smtplib
from datetime import datetime
from typing import Dict, List
from urllib.parse import urlparse
import re

class EcommercePriceMonitor:
    """电商价格监控器"""

    def __init__(self):
        self.targets = []
        self.history = []

    def add_target(self, name: str, url: str, target_price: float):
        """添加监控目标"""
        # 简单的平台检测
        if 'taobao.com' in url or 'tmall.com' in url:
            platform = '淘宝'
        elif 'jd.com' in url:
            platform = '京东'
        elif 'pinduoduo.com' in url:
            platform = '拼多多'
        else:
            platform = '通用'

        target = {
            'name': name,
            'url': url,
            'target_price': target_price,
            'platform': platform,
            'created_at': datetime.now().isoformat(),
            'status': 'active'
        }
        self.targets.append(target)
        print(f"✅ 已添加: {name} ({platform}) - 目标价: ¥{target_price}")

    def check_price(self, url: str) -> float:
        """
        检查价格（演示版，实际需要平台特定的解析逻辑）
        返回模拟价格用于演示
        """
        try:
            # 在实际应用中，这里应该：
            # 1. 访问URL获取HTML
            # 2. 根据平台提取价格
            # 3. 返回真实价格

            # 演示模式：返回一个基于URL的固定"价格"
            # 这样每次检查同一个商品都会得到相同结果
            url_hash = hash(url) % 1000
            simulated_price = 100 + (url_hash % 500)

            return round(simulated_price, 2)

        except Exception as e:
            print(f"❌ 获取价格失败: {e}")
            return 0.0

    def check_all(self):
        """检查所有目标"""
        print(f"\n{'='*60}")
        print(f"📊 价格检查报告")
        print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")

        deals = []

        for i, target in enumerate(self.targets, 1):
            if target['status'] != 'active':
                continue

            current_price = self.check_price(target['url'])
            target_price = target['target_price']

            # 计算价格差距
            diff = current_price - target_price
            discount = round((1 - current_price / (current_price + abs(diff))) * 100, 1)

            # 判断是否达标
            is_deal = current_price <= target_price

            if is_deal:
                deals.append(target)
                status_icon = "🎯 达标"
            elif discount > 0:
                status_icon = f"📉 降价 {discount}%"
            else:
                status_icon = "🔴 未达标"

            # 显示信息
            print(f"{i}. {target['name']}")
            print(f"   平台: {target['platform']}")
            print(f"   当前价: ¥{current_price}")
            print(f"   目标价: ¥{target_price}")
            print(f"   差价: ¥{diff:.2f}")
            print(f"   状态: {status_icon}")
            print()

        # 显示达标商品
        if deals:
            print("🎉 发现好价商品！")
            print("-" * 60)
            for deal in deals:
                print(f"✨ {deal['name']}")
                print(f"   链接: {deal['url']}")
                print(f"   平台: {deal['platform']}")
            print("-" * 60)

        return deals

    def export_config(self, filename: str = "monitor_config.json"):
        """导出配置"""
        config = {
            'targets': self.targets,
            'export_time': datetime.now().isoformat()
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        print(f"💾 配置已导出到: {filename}")

    def generate_report(self):
        """生成报告"""
        report = {
            'total_targets': len(self.targets),
            'active_targets': len([t for t in self.targets if t['status'] == 'active']),
            'platforms': list(set([t['platform'] for t in self.targets])),
            'generated_at': datetime.now().isoformat()
        }
        return report

def demo():
    """演示功能"""
    print("🛒 电商价格监控工具")
    print("=" * 60)
    print("\n演示模式：添加几个示例商品\n")

    monitor = EcommercePriceMonitor()

    # 添加示例目标
    examples = [
        {
            'name': 'iPhone 15 Pro',
            'url': 'https://detail.tmall.com/item.htm?id=example1',
            'target_price': 6999.00
        },
        {
            'name': '索尼 WH-1000XM5 耳机',
            'url': 'https://item.jd.com/example2',
            'target_price': 1899.00
        },
        {
            'name': '戴森吸尘器 V12',
            'url': 'https://detail.tmall.com/item.htm?id=example3',
            'target_price': 2999.00
        },
        {
            'name': 'Nike Air Max 270',
            'url': 'https://item.jd.com/example4',
            'target_price': 699.00
        }
    ]

    for item in examples:
        monitor.add_target(**item)

    # 执行检查
    print("🔍 开始价格检查...\n")
    monitor.check_all()

    # 显示统计
    print("\n📊 统计信息")
    print("-" * 60)
    report = monitor.generate_report()
    print(f"总目标数: {report['total_targets']}")
    print(f"活跃目标: {report['active_targets']}")
    print(f"覆盖平台: {', '.join(report['platforms'])}")

    # 导出配置
    monitor.export_config()

    print("\n" + "=" * 60)
    print("💡 使用提示：")
    print("1. 替换示例URL为真实商品链接")
    print("2. 修改 target_price 为你期望的价格")
    print("3. 可以定时运行此脚本检查价格")
    print("4. 达标后可以收到通知（需要配置邮件通知）")
    print("=" * 60)

if __name__ == "__main__":
    demo()
