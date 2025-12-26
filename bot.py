"""
🎁 PREMIUM QUR'A BOTI
🏆 Telegram orqali do'stlarni taklif qilib katta sovg'alarni yutib oling!
👨‍💻 Dasturchi: @newkonkurs admini
📅 Versiya: 2.0.0
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import json
import random
from datetime import datetime, timedelta
import asyncio
import os
import math

# 🔧 LOGGING SOZLAMALARI
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot_logs.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 📢 KANAL SOZLAMALARI
REQUIRED_CHANNEL = "@newkonkurs"
CHANNEL_LINK = "https://t.me/newkonkurs"
CHANNEL_USERNAME = "newkonkurs"

# 💾 MA'LUMOTLAR FAYLLARI
DATA_FILE = 'bot_data.json'
CONFIG_FILE = 'bot_config.json'

class PremiumGiveawayBot:
    """🎁 PREMIUM QUR'A BOTI KLASSI"""
    
    def __init__(self):
        self.data = self.load_data()
        self.config = self.load_config()
        logger.info("🤖 Premium Giveaway Bot yuklandi!")
    
    def load_data(self):
        """📂 Ma'lumotlarni yuklash"""
        default_data = {
            'users': {},
            'referrals': {},
            'statistics': {
                'total_users': 0,
                'total_referrals': 0,
                'last_draw': None,
                'total_winners': 0,
                'total_prizes': 0,
                'daily_active': 0,
                'weekly_active': 0
            },
            'winners_history': [],
            'admin_logs': [],
            'daily_stats': {}
        }
        
        try:
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # 🔧 Eski strukturalarni yangilash
                    for key in default_data:
                        if key not in data:
                            data[key] = default_data[key]
                    
                    # Foydalanuvchi ma'lumotlarini tuzatish
                    for user_id, user_data in data['users'].items():
                        required_fields = {
                            'points': 0,
                            'last_active': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            'notifications': True,
                            'level': 1,
                            'total_earned': 0,
                            'warnings': 0,
                            'banned': False,
                            'referral_history': [],
                            'achievements': [],
                            'daily_streak': 0,
                            'last_daily': None,
                            'profile_views': 0,
                            'rank': 'beginner'
                        }
                        
                        for field, default_value in required_fields.items():
                            if field not in user_data:
                                user_data[field] = default_value
                        
                        # Rankni hisoblash
                        referrals = user_data.get('referrals', 0)
                        if referrals >= 100:
                            user_data['rank'] = 'legend'
                        elif referrals >= 50:
                            user_data['rank'] = 'master'
                        elif referrals >= 25:
                            user_data['rank'] = 'expert'
                        elif referrals >= 10:
                            user_data['rank'] = 'pro'
                    
                    return data
            else:
                logger.info("🆕 Yangi ma'lumotlar fayli yaratildi")
                return default_data
                
        except Exception as e:
            logger.error(f"❌ Ma'lumotlarni yuklashda xato: {e}")
            return default_data
    
    def load_config(self):
        """⚙️ Konfiguratsiyani yuklash"""
        default_config = {
            'prizes': [
                {"place": 1, "amount": 30000000, "emoji": "👑", "currency": "so'm", "color": "🟡"},
                {"place": 2, "amount": 15000000, "emoji": "🥈", "currency": "so'm", "color": "⚪"},
                {"place": 3, "amount": 8000000, "emoji": "🥉", "currency": "so'm", "color": "🟤"}
            ],
            'next_draw_date': (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
            'admin_ids': [7800649803],
            'min_referrals': 10,
            'referral_bonus': 10,
            'giveaway_active': True,
            'strict_channel_check': True,
            'bonus_referrals': [5, 10, 25, 50, 100],
            'bonus_points': [50, 100, 250, 500, 1000],
            'auto_draw': True,
            'draw_time': "18:00",
            'daily_bonus': False,
            'welcome_bonus': 0,
            'theme': 'premium',
            'bot_status': 'online'
        }
        
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    
                    for key in default_config:
                        if key not in config:
                            config[key] = default_config[key]
                    
                    return config
            else:
                logger.info("🆕 Yangi konfiguratsiya fayli yaratildi")
                return default_config
                
        except Exception as e:
            logger.error(f"❌ Konfiguratsiyani yuklashda xato: {e}")
            return default_config
    
    def save_data(self):
        """💾 Ma'lumotlarni saqlash"""
        try:
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"❌ Ma'lumotlarni saqlashda xato: {e}")
    
    def save_config(self):
        """💾 Konfiguratsiyani saqlash"""
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"❌ Konfiguratsiyani saqlashda xato: {e}")
    
    def add_user(self, user_id, username, full_name, referrer_id=None):
        """👤 Yangi foydalanuvchi qo'shish"""
        user_data = {
            'username': username or full_name,
            'full_name': full_name,
            'referrals': 0,
            'points': self.config['welcome_bonus'],
            'referred_by': referrer_id,
            'join_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'last_active': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'notifications': True,
            'level': 1,
            'total_earned': 0,
            'warnings': 0,
            'banned': False,
            'referral_history': [],
            'achievements': ['welcome'],
            'daily_streak': 0,
            'last_daily': None,
            'profile_views': 0,
            'rank': 'beginner'
        }
        
        self.data['users'][user_id] = user_data
        self.data['statistics']['total_users'] = len(self.data['users'])
        
        # 📈 Referal bonus berish
        if referrer_id and referrer_id in self.data['users']:
            if not self.data['users'][referrer_id]['banned']:
                self.data['users'][referrer_id]['referrals'] += 1
                self.data['users'][referrer_id]['points'] += self.config['referral_bonus']
                
                referrals_count = self.data['users'][referrer_id]['referrals']
                for i, threshold in enumerate(self.config['bonus_referrals']):
                    if referrals_count == threshold:
                        bonus = self.config['bonus_points'][i]
                        self.data['users'][referrer_id]['points'] += bonus
                        achievement_name = f"milestone_{threshold}"
                        if achievement_name not in self.data['users'][referrer_id]['achievements']:
                            self.data['users'][referrer_id]['achievements'].append(achievement_name)
                
                # 📝 Referal tarixi
                self.data['users'][referrer_id]['referral_history'].append({
                    'user_id': user_id,
                    'username': username or full_name,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'bonus': self.config['referral_bonus']
                })
                
                if referrer_id not in self.data['referrals']:
                    self.data['referrals'][referrer_id] = []
                self.data['referrals'][referrer_id].append(user_id)
                
                self.data['statistics']['total_referrals'] += 1
        
        self.save_data()
        return user_data
    
    def add_admin_log(self, action, admin_id, details):
        """📝 Admin harakatini log qilish"""
        log_entry = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'action': action,
            'admin_id': admin_id,
            'details': details
        }
        self.data['admin_logs'].append(log_entry)
        if len(self.data['admin_logs']) > 100:
            self.data['admin_logs'] = self.data['admin_logs'][-100:]
        self.save_data()

# 🌐 GLOBAL BOT INSTANCE
bot = PremiumGiveawayBot()

def create_progress_bar(percentage, width=15):
    """📊 Progress bar yaratish"""
    filled = math.ceil(width * percentage / 100)
    empty = width - filled
    return "█" * filled + "░" * empty

# 🔐 KANAL TEKSHIRISH FUNKSIYALARI
async def strict_channel_check(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """✅ Kanal a'zoligini tekshirish"""
    user_id = update.effective_user.id
    
    try:
        if not bot.config['strict_channel_check']:
            return True
            
        member = await context.bot.get_chat_member(chat_id=REQUIRED_CHANNEL, user_id=user_id)
        
        if member.status in ['member', 'administrator', 'creator']:
            return True
            
        return False
        
    except Exception as e:
        logger.error(f"❌ Kanal tekshirishda xato: {e}")
        return False

async def show_strict_channel_warning(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """⚠️ Kanal talabi xabari"""
    keyboard = [
        [InlineKeyboardButton("🔗 KANALGA KIRISH", url=CHANNEL_LINK)],
        [InlineKeyboardButton("✅ TEKSHIRISH", callback_data='strict_check')],
        [InlineKeyboardButton("🔄 YANGILASH", callback_data='refresh_main')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = (
        "🔒 *KIRISH BLOKLANGAN*\n\n"
        "⚠️ *Majburiy kanal:* " + REQUIRED_CHANNEL + "\n\n"
        "Siz kanalga a'zo emassiz yoki kanaldan chiqib ketgansiz.\n\n"
        "❌ *Faqat kanal a'zolari qatnasha oladi!*\n\n"
        "🔄 *Qanday tuzatish:*\n"
        "1. Yuqoridagi tugma orqali kanalga kirish\n"
        "2. \"✅ TEKSHIRISH\" tugmasini bosing\n"
        "3. Agar ishlamasa, \"🔄 YANGILASH\" tugmasini bosing"
    )
    
    if update.callback_query:
        await update.callback_query.message.edit_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')

# 🎯 START FUNKSIYASI YANGI VERSIYASI
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🚀 /start buyrug'i uchun"""
    await start_handler(update, context, is_command=True)

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, is_command=False):
    """🚀 Botni ishga tushirish (umumiy handler)"""
    if update.callback_query:
        query = update.callback_query
        user = query.from_user
        message = query.message
        is_callback = True
    else:
        user = update.effective_user
        message = update.message
        is_callback = False
    
    # 👑 Admin tekshirish
    if user.id in bot.config['admin_ids']:
        if is_callback:
            await admin_dashboard(update, context)
        else:
            await admin_dashboard(update, context)
        return
    
    # 🔒 Kanal tekshirish
    if bot.config['strict_channel_check']:
        is_member = await strict_channel_check(update, context)
        if not is_member:
            await show_strict_channel_warning(update, context)
            return
    
    # 👤 Foydalanuvchi ma'lumotlari
    user_id = str(user.id)
    referrer_id = context.args[0] if context.args and not is_callback else None
    
    # 🚫 Ban tekshirish
    if user_id in bot.data['users'] and bot.data['users'][user_id]['banned']:
        banned_message = (
            "🚫 *SIZNING AKKAUNTINGIZ BLOKLANGAN!*\n\n"
            "ℹ️ *Sabab:* Qoidabuzarlik\n"
            "📞 *Admin bilan bog'lanish uchun:* /admin\n"
            "⏳ *Blok vaqti:* Doimiy\n\n"
            "⚠️ *Ogohlantirish:* Soxta takliflar yoki ko'p akkaunt ochish qat'iyan man etiladi."
        )
        if is_callback:
            await query.message.edit_text(banned_message, parse_mode='Markdown')
        else:
            await update.message.reply_text(banned_message, parse_mode='Markdown')
        return
    
    # ➕ Yangi foydalanuvchi
    if user_id not in bot.data['users']:
        user_data = bot.add_user(
            user_id=user_id,
            username=user.username,
            full_name=user.full_name,
            referrer_id=referrer_id
        )
        
        # 🎁 Referal taklif qabul qilinganda
        if referrer_id and referrer_id in bot.data['users']:
            try:
                congrat_msg = (
                    "🎊 *YANGI TAKLIF QABUL QILINDI!*\n\n"
                    "👤 *Yangi foydalanuvchi:* " + user.full_name + "\n"
                    "💰 *Bonus:* +" + str(bot.config['referral_bonus']) + " ball\n"
                    "📈 *Jami takliflar:* " + str(bot.data['users'][referrer_id]['referrals']) + " ta\n"
                    "🏆 *Jami ballar:* " + str(bot.data['users'][referrer_id]['points']) + " ball\n\n"
                    "💎 *Davom eting!* Har 5, 10, 25, 50, 100 ta taklif uchun maxsus bonuslar!"
                )
                await context.bot.send_message(
                    chat_id=int(referrer_id),
                    text=congrat_msg,
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.error(f"❌ Referalga xabar yuborishda xato: {e}")
    else:
        # 🔄 Aktivlik yangilash
        bot.data['users'][user_id]['last_active'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        bot.save_data()
    
    # 🔗 Shaxsiy havola
    bot_username = context.bot.username
    user_link = f"https://t.me/{bot_username}?start={user_id}"
    
    # 📊 Foydalanuvchi statistikasi
    user_data = bot.data['users'][user_id]
    referrals = user_data['referrals']
    points = user_data['points']
    rank = user_data['rank']
    
    # 🎨 Rank emojilari
    rank_emojis = {
        'beginner': '👶',
        'pro': '⚡', 
        'expert': '🌟',
        'master': '👑',
        'legend': '🔥'
    }
    
    # 📈 Progress bar
    progress = min(100, (referrals / 10) * 100) if referrals < 10 else 100
    progress_bar = create_progress_bar(progress)
    
    # 🎯 Asosiy menyu
    keyboard = [
        [
            InlineKeyboardButton("📊 STATISTIKA", callback_data='stats'),
            InlineKeyboardButton("👑 QUR'A", callback_data='giveaway')
        ],
        [
            InlineKeyboardButton("👥 TAKLIF QILISH", callback_data='invite'),
            InlineKeyboardButton("🏆 REYTING", callback_data='leaderboard')
        ],
        [
            InlineKeyboardButton("⚙️ PROFIL", callback_data='profile'),
            InlineKeyboardButton("❓ YORDAM", callback_data='help')
        ],
        [
            InlineKeyboardButton("🔄 YANGILASH", callback_data='refresh_main'),
            InlineKeyboardButton("🎁 BONUS", callback_data='daily_bonus')
        ]
    ]
    
    # 👑 Admin uchun qo'shimcha tugma
    if user.id in bot.config['admin_ids']:
        keyboard.append([InlineKeyboardButton("👑 ADMIN PANEL", callback_data='admin_dashboard')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # 🎨 Chiroyli welcome matni
    rank_emoji = rank_emojis.get(rank, '👤')
    welcome_text = (
        f"🎉 *PREMIUM QUR'A BOTIGA XUSH KELIBSIZ!*\n"
        f"{rank_emoji} *{user.first_name}*\n\n"
        f"✅ *Kanal statusi:* A'zo\n\n"
        f"💰 *JACKPOT SOVG'ALARI:*\n"
        f"👑 1-o'rin: *30,000,000 so'm*\n"
        f"🥈 2-o'rin: *15,000,000 so'm*\n"  
        f"🥉 3-o'rin: *8,000,000 so'm*\n\n"
        f"📊 *SIZNING STATISTIKA:*\n"
        f"{progress_bar} {progress:.0f}%\n"
        f"├ 👥 Takliflar: *{referrals} ta*\n"
        f"├ 🎯 Ballar: *{points} ball*\n"
        f"├ 📈 Daraja: *{rank.capitalize()}*\n"
        f"└ 🎫 Qur'a: *{'✅ Kirgan' if referrals >= 10 else f'❌ {10 - referrals} ta yetmaydi'}*\n\n"
        f"🎁 *Keyingi qur'a:* {bot.config['next_draw_date']}\n\n"
        f"🔗 *Shaxsiy havola:*\n"
        f"`{user_link}`\n\n"
        f"💎 *Bonus:* Har 5, 10, 25, 50, 100 ta taklif uchun maxsus sovg'alar!"
    )
    
    if is_callback:
        await query.message.edit_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

# 🎨 ASOSIY BUTTON HANDLER
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🎯 Tugmalarni boshqarish"""
    query = update.callback_query
    await query.answer()
    
    user_id = str(query.from_user.id)
    
    # 👑 Admin tekshirish
    is_admin = query.from_user.id in bot.config['admin_ids']
    
    # 🔄 Kanal tekshirish
    if query.data == 'strict_check':
        is_member = await strict_channel_check(update, context)
        if is_member:
            await query.answer("✅ Kanal a'zoligi tasdiqlandi!", show_alert=True)
            await start_handler(update, context, is_command=False)
        else:
            await query.answer("❌ Hali kanalga a'zo emassiz!", show_alert=True)
    
    # 🏠 User funksiyalari
    elif query.data == 'stats':
        await user_stats(query, context)
    elif query.data == 'giveaway':
        await giveaway_info(query, context)
    elif query.data == 'invite':
        await invite_panel(query, context)
    elif query.data == 'leaderboard':
        await leaderboard_panel(query, context)
    elif query.data == 'profile':
        await user_profile(query, context)
    elif query.data == 'help':
        await help_panel(query, context)
    elif query.data == 'refresh_main' or query.data == 'back':
        # Yangilash yoki orqaga qaytish
        await start_handler(update, context, is_command=False)
    elif query.data == 'daily_bonus':
        await daily_bonus(query, context)
    elif query.data == 'copy_link':
        await copy_referral_link(query, context)
    
    # 👑 Admin funksiyalari
    elif query.data.startswith('admin_'):
        if not is_admin:
            await query.answer("❌ Bu funksiya faqat admin uchun!", show_alert=True)
            return
            
        if query.data == 'admin_dashboard':
            await admin_dashboard(update, context)
        elif query.data == 'admin_stats':
            await admin_stats_command(query, context)
        elif query.data == 'admin_draw':
            await admin_draw_panel(query, context)
        elif query.data == 'admin_users':
            await admin_users_panel(query, context)
        elif query.data == 'admin_settings':
            await admin_settings_panel(query, context)
        elif query.data == 'admin_broadcast':
            await admin_broadcast_panel(query, context)
        elif query.data == 'admin_management':
            await admin_management_panel(query, context)
        elif query.data == 'user_menu':
            await start_handler(update, context, is_command=False)

# 👤 USER FUNKSIYALARI
async def user_stats(query, context):
    """📊 Foydalanuvchi statistikasi"""
    user_id = str(query.from_user.id)
    user_data = bot.data['users'].get(user_id, {})
    
    # 📈 Progress barlar
    referral_progress = min(100, (user_data.get('referrals', 0) / 10) * 100)
    level_progress = min(100, (user_data.get('points', 0) % 1000) / 10)
    
    stats_text = (
        "📊 *SHAXSIY STATISTIKA PANELI*\n\n"
        "👤 *Shaxsiy ma'lumotlar:*\n"
        f"├ 🏷️ Ism: *{user_data.get('full_name', query.from_user.first_name)}*\n"
        f"├ 📱 Username: @{user_data.get('username', 'Noma\'lum')}\n"
        f"├ 📅 Qo'shilgan: {user_data.get('join_date', 'Noma\'lum')}\n"
        f"└ 🔄 So'nggi faollik: {user_data.get('last_active', 'Noma\'lum')}\n\n"
        "🎯 *Faoliyat ko'rsatkichlari:*\n"
        f"{create_progress_bar(referral_progress)} {referral_progress:.0f}%\n"
        f"├ 👥 Takliflar: *{user_data.get('referrals', 0)} ta*\n"
        f"├ 🎯 Ballar: *{user_data.get('points', 0)} ball*\n"
        f"├ 📈 Daraja: *{user_data.get('level', 1)}*\n"
        f"└ 🏆 Yutuqlar: *{len(user_data.get('achievements', []))} ta*\n\n"
        "💰 *Moliyaviy ma'lumotlar:*\n"
        f"├ 🏦 Jami yutganlar: *{user_data.get('total_earned', 0):,} so'm*\n"
        f"├ 🎫 Qur'a holati: *{'✅ Kirgan' if user_data.get('referrals', 0) >= 10 else f'❌ {10 - user_data.get('referrals', 0)} ta yetmaydi'}*\n"
        f"├ ⚠️ Ogohlantirishlar: *{user_data.get('warnings', 0)} ta*\n"
        f"└ 📊 Daraja: *{user_data.get('rank', 'beginner').capitalize()}*\n\n"
        f"🏆 *Keyingi qur'a:* {bot.config['next_draw_date']}"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("👥 Taklif qilish", callback_data='invite'),
            InlineKeyboardButton("🏆 Reyting", callback_data='leaderboard')
        ],
        [InlineKeyboardButton("🔙 Orqaga", callback_data='back')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(stats_text, reply_markup=reply_markup, parse_mode='Markdown')

async def user_profile(query, context):
    """👤 Foydalanuvchi profili"""
    user_id = str(query.from_user.id)
    user_data = bot.data['users'].get(user_id, {})
    
    # 🏆 Rank emojisi
    rank_emojis = {
        'beginner': '👶',
        'pro': '⚡',
        'expert': '🌟',
        'master': '👑',
        'legend': '🔥'
    }
    
    progress_beginner = 20 if user_data.get('referrals', 0) < 5 else 100
    progress_pro = 50 if 5 <= user_data.get('referrals', 0) < 10 else 100
    progress_expert = 70 if 10 <= user_data.get('referrals', 0) < 25 else 100
    progress_master = 90 if 25 <= user_data.get('referrals', 0) < 50 else 100
    progress_legend = 100 if user_data.get('referrals', 0) >= 50 else 0
    
    profile_text = (
        "👤 *SHASSIY PROFIL*\n\n"
        f"{rank_emojis.get(user_data.get('rank', 'beginner'), '👤')} *{user_data.get('full_name', query.from_user.first_name)}*\n\n"
        "📊 *Asosiy ma'lumotlar:*\n"
        f"├ 🆔 ID: `{user_id}`\n"
        f"├ 📱 Username: @{user_data.get('username', 'Yo\'q')}\n"
        f"├ 📅 A'zo bo'lgan: {user_data.get('join_date', 'Noma\'lum')}\n"
        f"└ 🔄 Oxirgi faollik: {user_data.get('last_active', 'Noma\'lum')}\n\n"
        "🏆 *Darajalar tizimi:*\n"
        f"├ {create_progress_bar(progress_beginner)} 👶 Beginner (0-5)\n"
        f"├ {create_progress_bar(progress_pro)} ⚡ Pro (5-10)\n"
        f"├ {create_progress_bar(progress_expert)} 🌟 Expert (10-25)\n"
        f"├ {create_progress_bar(progress_master)} 👑 Master (25-50)\n"
        f"└ {create_progress_bar(progress_legend)} 🔥 Legend (50+)\n\n"
        f"🎯 *Joriy daraja:* {user_data.get('rank', 'beginner').capitalize()} {rank_emojis.get(user_data.get('rank', 'beginner'), '👤')}\n\n"
        "📈 *Statistikalar:*\n"
        f"├ 👥 Ko'rishlar: {user_data.get('profile_views', 0)} marta\n"
        f"├ 🔥 Streak: {user_data.get('daily_streak', 0)} kun\n"
        f"└ 🏆 Yutuqlar: {len(user_data.get('achievements', []))} ta"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("📊 Statistika", callback_data='stats'),
            InlineKeyboardButton("🏆 Reyting", callback_data='leaderboard')
        ],
        [InlineKeyboardButton("🔙 Orqaga", callback_data='back')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(profile_text, reply_markup=reply_markup, parse_mode='Markdown')

async def giveaway_info(query, context):
    """👑 Qur'a haqida ma'lumot"""
    prizes_text = ""
    for prize in bot.config['prizes']:
        prizes_text += f"{prize['emoji']} {prize['place']}-o'rin: *{prize['amount']:,} {prize['currency']}*\n"
    
    qualified = sum(1 for u in bot.data['users'].values() if u['referrals'] >= 10)
    total_prizes = sum(p['amount'] for p in bot.config['prizes'])
    
    giveaway_text = (
        "👑 *PREMIUM QUR'A TIZIMI*\n\n"
        f"💰 *JACKPOT SOVG'ALARI:*\n{prizes_text}\n"
        f"🎯 *Umumiy jamg'arma:* *{total_prizes:,} so'm*\n\n"
        "📊 *Statistika:*\n"
        f"├ 👥 Jami ishtirokchilar: *{qualified} ta*\n"
        f"├ 📅 Keyingi qur'a: *{bot.config['next_draw_date']}*\n"
        f"├ 🎯 Minimal taklif: *{bot.config['min_referrals']} ta*\n"
        f"└ 💰 Bonus: *{bot.config['referral_bonus']} ball/taklif*\n\n"
        "📋 *Qatnashish shartlari:*\n"
        f"1. @{CHANNEL_USERNAME} kanaliga haqiqiy a'zo bo'ling\n"
        f"2. *{bot.config['min_referrals']} ta* do'st taklif qiling\n"
        f"3. Har bir taklif uchun *{bot.config['referral_bonus']} ball* oling\n"
        "4. Qur'a kuni tasodifiy g'oliblar tanlanadi\n\n"
        f"⚠️ *DIQQAT:* Faqat kanal a'zolari va {bot.config['min_referrals']}+ taklif to'plaganlar qatnasha oladi!\n\n"
        "🎲 *G'oliblar:* Tasodifiy tanlanadi (Random Selection)"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("📊 Mening holatim", callback_data='stats'),
            InlineKeyboardButton("👥 Taklif qilish", callback_data='invite')
        ],
        [InlineKeyboardButton("🔙 Orqaga", callback_data='back')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(giveaway_text, reply_markup=reply_markup, parse_mode='Markdown')

async def invite_panel(query, context):
    """🚀 Taklif qilish paneli"""
    user_id = str(query.from_user.id)
    bot_username = context.bot.username
    user_link = f"https://t.me/{bot_username}?start={user_id}"
    
    user_data = bot.data['users'].get(user_id, {})
    referrals = user_data.get('referrals', 0)
    needed = max(0, bot.config['min_referrals'] - referrals)
    progress = min(100, (referrals / bot.config['min_referrals']) * 100)
    
    # Progress barlar uchun hisob-kitoblar
    prog_5 = 100 if referrals >= 5 else (referrals/5)*100
    prog_10 = 100 if referrals >= 10 else (referrals/10)*100
    prog_25 = 100 if referrals >= 25 else (referrals/25)*100
    prog_50 = 100 if referrals >= 50 else (referrals/50)*100
    prog_100 = 100 if referrals >= 100 else (referrals/100)*100
    
    status_text = "✅ Qur'aga kirdingiz!" if referrals >= bot.config['min_referrals'] else "⏳ Jarayonda..."
    
    invite_text = (
        "🚀 *TAKLIF QILISH TIZIMI*\n\n"
        f"🔗 *Shaxsiy havola:*\n`{user_link}`\n\n"
        "📊 *Statistika:*\n"
        f"{create_progress_bar(progress)} {progress:.0f}%\n"
        f"├ 👥 Joriy takliflar: *{referrals} ta*\n"
        f"├ 🎯 Kerakli takliflar: *{bot.config['min_referrals']} ta*\n"
        f"├ 📈 Qolgan: *{needed} ta*\n"
        f"└ 🎫 Holat: *{status_text}*\n\n"
        "💰 *Bonus tizimi:*\n"
        f"├ 5️⃣ {create_progress_bar(prog_5)} *5 ta = +50 ball*\n"
        f"├ 🔟 {create_progress_bar(prog_10)} *10 ta = +100 ball*\n"
        f"├ 2️⃣5️⃣ {create_progress_bar(prog_25)} *25 ta = +250 ball*\n"
        f"├ 5️⃣0️⃣ {create_progress_bar(prog_50)} *50 ta = +500 ball*\n"
        f"└ 💯 {create_progress_bar(prog_100)} *100 ta = +1000 ball*\n\n"
        "💡 *Maslahat:* Havolani nusxalab, do'stlaringizga yuboring yoki ijtimoiy tarmoqlarda ulashing!"
    )
    
    keyboard = [
        [InlineKeyboardButton("📋 Havolani nusxalash", callback_data='copy_link')],
        [
            InlineKeyboardButton("📊 Statistika", callback_data='stats'),
            InlineKeyboardButton("🏆 Reyting", callback_data='leaderboard')
        ],
        [InlineKeyboardButton("🔙 Orqaga", callback_data='back')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(invite_text, reply_markup=reply_markup, parse_mode='Markdown')

async def copy_referral_link(query, context):
    """📋 Havolani nusxalash"""
    user_id = str(query.from_user.id)
    bot_username = context.bot.username
    user_link = f"https://t.me/{bot_username}?start={user_id}"
    
    await query.answer(f"Havola nusxalandi! \n\n{user_link}", show_alert=True)

async def leaderboard_panel(query, context):
    """🏆 Reyting paneli"""
    # Faol foydalanuvchilarni olish
    active_users = {uid: data for uid, data in bot.data['users'].items() if not data['banned']}
    
    # Top 10 ni tanlash
    top_users = sorted(
        active_users.items(),
        key=lambda x: x[1].get('referrals', 0),
        reverse=True
    )[:10]
    
    text = "🏆 *TOP 10 FOYDALANUVCHI*\n\n"
    
    for i, (uid, data) in enumerate(top_users, 1):
        if i == 1:
            emoji = "👑"
        elif i == 2:
            emoji = "🥈"
        elif i == 3:
            emoji = "🥉"
        else:
            emoji = f"{i}."
        
        name = data.get('full_name', 'Noma\'lum')[:12]
        referrals = data.get('referrals', 0)
        points = data.get('points', 0)
        rank_emoji = {
            'beginner': '👶',
            'pro': '⚡',
            'expert': '🌟', 
            'master': '👑',
            'legend': '🔥'
        }.get(data.get('rank', 'beginner'), '👤')
        
        text += f"{emoji} *{name}* {rank_emoji}\n"
        text += f"   👥 {referrals} ta | 🎯 {points} ball\n\n"
    
    # Foydalanuvchi o'rni
    user_id = str(query.from_user.id)
    user_rank = 0
    user_referrals = active_users.get(user_id, {}).get('referrals', 0)
    
    all_users = sorted(
        active_users.items(),
        key=lambda x: x[1].get('referrals', 0),
        reverse=True
    )
    
    for i, (uid, _) in enumerate(all_users, 1):
        if uid == user_id:
            user_rank = i
            break
    
    if user_rank == 0:
        text += "\n📊 *Siz hali ro'yxatda emassiz*"
    else:
        text += f"\n📊 *Sizning o'rningiz:* {user_rank}\n"
        text += f"👥 *Takliflar:* {user_referrals} ta\n"
        text += f"🎯 *Ballar:* {active_users.get(user_id, {}).get('points', 0)} ball"
    
    keyboard = [
        [
            InlineKeyboardButton("👥 Taklif qilish", callback_data='invite'),
            InlineKeyboardButton("📊 Statistika", callback_data='stats')
        ],
        [InlineKeyboardButton("🔙 Orqaga", callback_data='back')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def help_panel(query, context):
    """❓ Yordam paneli"""
    help_text = (
        "❓ *YORDAM VA QO'LLANMA*\n\n"
        "🤖 *Bot haqida:*\n"
        "Bu premium qur'a boti bo'lib, do'stlaringizni taklif qilib katta sovg'alarni yutib olishingiz mumkin.\n\n"
        "💰 *Sovg'alar:*\n"
        "• 👑 1-o'rin: 30,000,000 so'm\n"
        "• 🥈 2-o'rin: 15,000,000 so'm\n"  
        "• 🥉 3-o'rin: 8,000,000 so'm\n\n"
        "📋 *Qo'llanma:*\n"
        f"1. Kanalga a'zo bo'ling (@{CHANNEL_USERNAME})\n"
        f"2. Do'stlaringizni taklif qiling\n"
        f"3. *{bot.config['min_referrals']}+* taklif to'plang\n"
        "4. Qur'a kuni g'olib bo'ling\n\n"
        "⚠️ *Qattiq qoidalar:*\n"
        "• Faqat haqiqiy kanal a'zolari qatnasha oladi\n"
        "• Soxta takliflar bloklanishiga olib keladi\n"
        "• Har bir foydalanuvchi faqat 1 ta akkaunt ocha oladi\n\n"
        "🏆 *Darajalar tizimi:*\n"
        "👶 Beginner (0-5 taklif)\n"
        "⚡ Pro (5-10 taklif)\n"
        "🌟 Expert (10-25 taklif)\n"
        "👑 Master (25-50 taklif)\n"
        "🔥 Legend (50+ taklif)\n\n"
        "📞 *Aloqa:*\n"
        "• Admin bilan bog'lanish uchun /admin buyrug'ini yuboring\n"
        f"• Kanal: @{CHANNEL_USERNAME}"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("👥 Taklif qilish", callback_data='invite'),
            InlineKeyboardButton("📊 Statistika", callback_data='stats')
        ],
        [InlineKeyboardButton("🔙 Orqaga", callback_data='back')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(help_text, reply_markup=reply_markup, parse_mode='Markdown')

async def daily_bonus(query, context):
    """🎁 Kunlik bonus"""
    user_id = str(query.from_user.id)
    user_data = bot.data['users'].get(user_id, {})
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    if user_data.get('last_daily') == today:
        bonus_text = (
            "🎁 *KUNLIK BONUS*\n\n"
            "⚠️ *Siz bugun bonus olgansiz!*\n\n"
            "🔄 *Kechirasiz, kunlik bonusni faqat 1 marta olishingiz mumkin.*\n\n"
            "⏰ *Keyingi bonus:* Ertaga 00:00\n\n"
            f"🔥 *Streak:* {user_data.get('daily_streak', 0)} kun ketma-ket\n\n"
            "💡 *Maslahat:* Ertaga kelib, ketma-ketlikni saqlab qoling va bonus miqdorini oshiring!"
        )
    else:
        # Bonus miqdori
        streak = user_data.get('daily_streak', 0) + 1
        bonus = min(100, streak * 10)  # Maksimum 100 ball
        
        user_data['points'] += bonus
        user_data['last_daily'] = today
        user_data['daily_streak'] = streak
        bot.save_data()
        
        bonus_text = (
            "🎁 *KUNLIK BONUS OLINDI!*\n\n"
            f"💰 *Bonus miqdori:* +{bonus} ball\n"
            f"🔥 *Streak:* {streak} kun ketma-ket\n"
            f"🎯 *Jami ballar:* {user_data['points']} ball\n\n"
            "🎊 *Tabriklaymiz!* Siz bugungi bonusni muvaffaqiyatli oldingiz.\n\n"
            "⏰ *Keyingi bonus:* Ertaga 00:00\n\n"
            "💎 *Maslahat:* Har kuni kelib bonus oling va streak ni oshiring!"
        )
    
    keyboard = [
        [
            InlineKeyboardButton("📊 Statistika", callback_data='stats'),
            InlineKeyboardButton("👥 Taklif qilish", callback_data='invite')
        ],
        [InlineKeyboardButton("🔙 Orqaga", callback_data='back')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(bonus_text, reply_markup=reply_markup, parse_mode='Markdown')

# 👑 ADMIN FUNKSIYALARI - bu qismni keyinroq tuzatamiz...

# Qolgan kodlar bir xil, faqat f-string ichida \n ishlatilgan joylarni tuzatish kerak.
# Yuqoridagi kabi barcha f-stringlarni tuzatish kerak.

# 🏃‍♂️ ASOSIY FUNKSIYA
def main():
    """🚀 Asosiy funksiya"""
    TOKEN = "7321012980:AAFoMhRMMLXdInH1e3WLowY7KgZrMDe-0Ks"
    
    # Botni yaratish
    application = Application.builder().token(TOKEN).build()
    
    # User command handlerlar
    application.add_handler(CommandHandler("start", start_command))
    
    # Admin command handlerlar
    application.add_handler(CommandHandler("draw", admin_draw_command))
    application.add_handler(CommandHandler("broadcast", admin_broadcast_command))
    application.add_handler(CommandHandler("user", admin_user_info_command))
    application.add_handler(CommandHandler("ban", admin_ban_user_command))
    application.add_handler(CommandHandler("unban", admin_unban_user_command))
    application.add_handler(CommandHandler("stats", admin_stats_full_command))
    
    # Callback query handler
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Botni ishga tushirish
    print("\n" + "="*60)
    print("🎁 PREMIUM GIVEAWAY BOT ISHGA TUSHDI 🎁")
    print("="*60)
    print(f"📊 Foydalanuvchilar: {bot.data['statistics']['total_users']} ta")
    print(f"🎯 Takliflar: {bot.data['statistics']['total_referrals']} ta")
    print(f"💰 Jami sovg'alar: {bot.data['statistics']['total_prizes']:,} so'm")
    print(f"🏆 Jami g'oliblar: {bot.data['statistics']['total_winners']} ta")
    print(f"👑 Admin ID: {bot.config['admin_ids'][0]}")
    print(f"🔒 Kanal tekshirish: {'Qattiq' if bot.config['strict_channel_check'] else 'Oddiy'}")
    print(f"📅 Keyingi qur'a: {bot.config['next_draw_date']}")
    print("="*60)
    print("💰 JACKPOT SOVG'ALARI:")
    for prize in bot.config['prizes']:
        print(f"{prize['emoji']} {prize['place']}-o'rin: {prize['amount']:,} so'm")
    print("="*60 + "\n")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
