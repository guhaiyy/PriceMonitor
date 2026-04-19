#!/usr/bin/env python3
"""
邮件通知模块
当价格达标时发送邮件提醒
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from typing import List, Dict
import json
from datetime import datetime
import os

class EmailNotifier:
    """邮件通知器"""

    def __init__(self, config_file: str = "email_config.json"):
        self.config_file = config_file
        self.config = {}
        self.load_config()

    def load_config(self):
        """加载邮件配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
        except Exception as e:
            print(f"⚠️  加载邮件配置失败: {e}")
            self.config = {}

    def save_config(self):
        """保存邮件配置"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

    def setup(self, smtp_host: str, smtp_port: int, smtp_user: str,
              smtp_password: str, from_email: str, from_name: str = "价格监控"):
        """配置邮件服务器"""
        self.config = {
            'smtp_host': smtp_host,
            'smtp_port': smtp_port,
            'smtp_user': smtp_user,
            'smtp_password': smtp_password,
            'from_email': from_email,
            'from_name': from_name,
            'setup_at': datetime.now().isoformat()
        }
        self.save_config()
        print("✅ 邮件配置已保存")

    def test_connection(self) -> bool:
        """测试邮件连接"""
        if not self.config:
            print("❌ 邮件未配置")
            return False

        try:
            with smtplib.SMTP_SSL(self.config['smtp_host'],
                                  self.config['smtp_port'], timeout=10) as server:
                server.login(self.config['smtp_user'], self.config['smtp_password'])
            print("✅ 邮件连接测试成功")
            return True
        except Exception as e:
            print(f"❌ 邮件连接测试失败: {e}")
            return False

    def send_alert(self, to_email: str, deals: List[Dict]) -> bool:
        """发送价格提醒邮件"""
        if not self.config:
            print("❌ 邮件未配置，无法发送提醒")
            return False

        if not deals:
            print("⚠️  没有达标的商品")
            return False

        try:
            # 创建邮件
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"🎉 价格监控提醒 - {len(deals)}个商品已达标！"
            msg['From'] = f"{self.config['from_name']} <{self.config['from_email']}>"
            msg['To'] = to_email

            # 邮件正文
            html_content = self._generate_html(deals)
            text_content = self._generate_text(deals)

            part1 = MIMEText(text_content, 'plain', 'utf-8')
            part2 = MIMEText(html_content, 'html', 'utf-8')

            msg.attach(part1)
            msg.attach(part2)

            # 发送邮件
            with smtplib.SMTP_SSL(self.config['smtp_host'],
                                  self.config['smtp_port'], timeout=10) as server:
                server.login(self.config['smtp_user'], self.config['smtp_password'])
                server.send_message(msg)

            print(f"✅ 邮件已发送至: {to_email}")
            return True

        except Exception as e:
            print(f"❌ 邮件发送失败: {e}")
            return False

    def _generate_text(self, deals: List[Dict]) -> str:
        """生成纯文本内容"""
        lines = []
        lines.append("🎉 价格监控提醒")
        lines.append("=" * 60)
        lines.append(f"\n发现 {len(deals)} 个商品已达到目标价格！\n")

        for i, deal in enumerate(deals, 1):
            lines.append(f"{i}. {deal['name']}")
            lines.append(f"   平台: {deal['platform']}")
            lines.append(f"   当前价格: ¥{deal['current_price']}")
            lines.append(f"   目标价格: ¥{deal['target_price']}")
            lines.append(f"   链接: {deal['url']}")
            lines.append("")

        lines.append("=" * 60)
        lines.append("立即购买，错过再等一年！")
        lines.append("\n---")
        lines.append("此邮件由价格监控工具自动发送")

        return '\n'.join(lines)

    def _generate_html(self, deals: List[Dict]) -> str:
        """生成HTML内容"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9f9f9; padding: 20px; border-radius: 0 0 10px 10px; }}
        .deal-item {{ background: white; padding: 15px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .deal-name {{ font-size: 18px; font-weight: bold; color: #667eea; }}
        .deal-price {{ font-size: 24px; color: #28a745; font-weight: bold; }}
        .deal-platform {{ background: #e9ecef; padding: 5px 10px; border-radius: 20px; font-size: 14px; }}
        .btn {{ display: inline-block; padding: 10px 20px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin-top: 10px; }}
        .footer {{ text-align: center; margin-top: 20px; color: #999; font-size: 14px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 价格监控提醒</h1>
            <p>发现 <strong>{len(deals)}</strong> 个商品已达到目标价格！</p>
        </div>
        <div class="content">
"""

        for deal in deals:
            savings = deal.get('target_price', deal['current_price']) - deal['current_price']
            html += f"""
            <div class="deal-item">
                <div class="deal-name">{deal['name']}</div>
                <div style="margin: 10px 0;">
                    <span class="deal-platform">{deal['platform']}</span>
                    <span style="margin-left: 10px; color: #999;">💰 省约 ¥{abs(savings):.2f}</span>
                </div>
                <div style="display: flex; align-items: baseline; justify-content: space-between;">
                    <div>
                        <span style="color: #999;">当前价格：</span>
                        <span class="deal-price">¥{deal['current_price']:.2f}</span>
                    </div>
                    <div>
                        <span style="color: #999;">目标价格：</span>
                        <span style="font-size: 18px;">¥{deal.get('target_price', 0):.2f}</span>
                    </div>
                </div>
                <a href="{deal['url']}" class="btn" target="_blank">🛒 立即购买</a>
            </div>
"""

        html += f"""
        </div>
        <div class="footer">
            <p>此邮件由价格监控工具自动发送</p>
            <p>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>
"""
        return html

    def send_summary(self, to_email: str, targets: List[Dict]) -> bool:
        """发送监控摘要"""
        if not self.config:
            return False

        try:
            active = [t for t in targets if t.get('status') == 'active']
            deals = [t for t in active if t.get('current_price', float('inf')) <= t.get('target_price', float('inf'))]

            subject = f"📊 价格监控摘要 - {len(active)}个监控中，{len(deals)}个已达标"

            msg = MIMEText(
                f"价格监控摘要\n"
                f"总监控数: {len(targets)}\n"
                f"活跃监控: {len(active)}\n"
                f"达标商品: {len(deals)}\n\n"
                f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                'plain', 'utf-8'
            )
            msg['Subject'] = subject
            msg['From'] = f"{self.config['from_name']} <{self.config['from_email']}>"
            msg['To'] = to_email

            with smtplib.SMTP_SSL(self.config['smtp_host'],
                                  self.config['smtp_port'], timeout=10) as server:
                server.login(self.config['smtp_user'], self.config['smtp_password'])
                server.send_message(msg)

            print(f"✅ 摘要已发送至: {to_email}")
            return True

        except Exception as e:
            print(f"❌ 摘要发送失败: {e}")
            return False


# 使用示例
if __name__ == "__main__":
    notifier = EmailNotifier()

    # 配置示例（实际使用时填写真实信息）
    print("📧 邮件通知模块")
    print("=" * 60)
    print("\n配置示例:")
    print("""
    notifier.setup(
        smtp_host="smtp.qq.com",      # QQ邮箱
        smtp_port=465,
        smtp_user="your@qq.com",
        smtp_password="授权码",       # 不是密码，是SMTP授权码
        from_email="your@qq.com",
        from_name="价格监控助手"
    )
    """)

    print("\n💡 获取SMTP授权码:")
    print("QQ邮箱: 设置 -> 账户 -> POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务")
    print("163邮箱: 设置 -> POP3/SMTP/IMAP")
    print("Gmail: 账户设置 -> 安全性 -> 两步验证 -> 应用密码")

    print("\n" + "=" * 60)
