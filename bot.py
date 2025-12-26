"""
🎁 PREMIUM QUR'A BOTI - QISM 1
🏆 Telegram orqali do'stlarni taklif qilib katta sovg'alarni yutib oling!
👨‍💻 Dasturchi: @newkonkurs admini
📅 Versiya: 2.0.1 (FIXED)
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
                    
                    for key in default_data:
                        if key not in data:
                            data[key] = default_data[key]
                    
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
        [InlineKeyboardButton("🔄 YANGILASH", callback_data='refresh')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = f"""
🔒 *KIRISH BLOKLANGAN*

⚠️ *Majburiy kanal:* {REQUIRED_CHANNEL}

Siz kanalga a'zo emassiz yoki kanaldan chiqib ketgansiz.

❌ *Faqat kanal a'zolari qatnasha oladi!*

🔄 *Qanday tuzatish:*
1. Yuqoridagi tugma orqali kanalga kirish
2. "✅ TEKSHIRISH" tugmasini bosing
3. Agar ishlamasa, "🔄 YANGILASH" tugmasini bosing
"""
    
    if update.callback_query:
        await update.callback_query.message.edit_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
# 🎯 ASOSIY START FUNKSIYASI
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🚀 Botni ishga tushirish"""
    # FIXED: callback_query dan kelgan so'rovlarni to'g'ri handle qilish
    if update.callback_query:
        query = update.callback_query
        user = query.from_user
        is_callback = True
    else:
        user = update.effective_user
        is_callback = False
    
    # 👑 Admin tekshirish
    if user.id in bot.config['admin_ids']:
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
    referrer_id = None
    
    if not is_callback and context.args:
        referrer_id = context.args[0]
    
    # 🚫 Ban tekshirish
    if user_id in bot.data['users'] and bot.data['users'][user_id]['banned']:
        banned_message = """
🚫 *SIZNING AKKAUNTINGIZ BLOKLANGAN!*

ℹ️ *Sabab:* Qoidabuzarlik
⏳ *Blok vaqti:* Doimiy

⚠️ *Ogohlantirish:* Soxta takliflar yoki ko'p akkaunt ochish qat'iyan man etiladi.
"""
        
        if is_callback:
            await query.edit_message_text(banned_message, parse_mode='Markdown')
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
        
        if referrer_id and referrer_id in bot.data['users']:
            try:
                congrat_msg = f"""
🎊 *YANGI TAKLIF QABUL QILINDI!*

👤 *Yangi foydalanuvchi:* {user.full_name}
💰 *Bonus:* +{bot.config['referral_bonus']} ball
📈 *Jami takliflar:* {bot.data['users'][referrer_id]['referrals']} ta
🏆 *Jami ballar:* {bot.data['users'][referrer_id]['points']} ball

💎 *Davom eting!* Har 5, 10, 25, 50, 100 ta taklif uchun maxsus bonuslar!
"""
                await context.bot.send_message(
                    chat_id=int(referrer_id),
                    text=congrat_msg,
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.error(f"❌ Referalga xabar yuborishda xato: {e}")
    else:
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
    
    rank_emojis = {
        'beginner': '👶',
        'pro': '⚡', 
        'expert': '🌟',
        'master': '👑',
        'legend': '🔥'
    }
    
    progress = min(100, (referrals / 10) * 100) if referrals < 10 else 100
    progress_bar = create_progress_bar(progress)
    
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
            InlineKeyboardButton("🔄 YANGILASH", callback_data='refresh'),
            InlineKeyboardButton("🎁 BONUS", callback_data='daily_bonus')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = f"""
🎉 *PREMIUM QUR'A BOTIGA XUSH KELIBSIZ!*
{rank_emojis.get(rank, '👤')} *{user.first_name}*

✅ *Kanal statusi:* A'zo

💰 *JACKPOT SOVG'ALARI:*
👑 1-o'rin: *30,000,000 so'm*
🥈 2-o'rin: *15,000,000 so'm*  
🥉 3-o'rin: *8,000,000 so'm*

📊 *SIZNING STATISTIKA:*
{progress_bar} {progress:.0f}%
├ 👥 Takliflar: *{referrals} ta*
├ 🎯 Ballar: *{points} ball*
├ 📈 Daraja: *{rank.capitalize()}*
└ 🎫 Qur'a: *{'✅ Kirgan' if referrals >= 10 else f'❌ {10 - referrals} ta yetmaydi'}*

🎁 *Keyingi qur'a:* {bot.config['next_draw_date']}

🔗 *Shaxsiy havola:*
`{user_link}`

💎 *Bonus:* Har 5, 10, 25, 50, 100 ta taklif uchun maxsus sovg'alar!
"""
    
    if is_callback:
        await query.edit_message_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')


# 🎨 ASOSIY BUTTON HANDLER
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🎯 Tugmalarni boshqarish"""
    query = update.callback_query
    await query.answer()
    
    user_id = str(query.from_user.id)
    is_admin = query.from_user.id in bot.config['admin_ids']
    
    if query.data == 'strict_check':
        is_member = await strict_channel_check(update, context)
        if is_member:
            await query.answer("✅ Kanal a'zoligi tasdiqlandi!", show_alert=True)
            await start(update, context)
        else:
            await query.answer("❌ Hali kanalga a'zo emassiz!", show_alert=True)
        return
    
    # 🏠 User funksiyalari
    if query.data == 'stats':
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
    elif query.data == 'refresh' or query.data == 'back':
        await start(update, context)
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
            await start(update, context)
        elif query.data == 'execute_draw':
            await execute_draw_from_callback(query, context)


# 👤 USER FUNKSIYALARI
async def user_stats(query, context):
    """📊 Foydalanuvchi statistikasi"""
    user_id = str(query.from_user.id)
    user_data = bot.data['users'].get(user_id, {})
    
    referral_progress = min(100, (user_data.get('referrals', 0) / 10) * 100)
    
    stats_text = f"""
📊 *SHAXSIY STATISTIKA PANELI*

👤 *Shaxsiy ma'lumotlar:*
├ 🏷️ Ism: *{user_data.get('full_name', query.from_user.first_name)}*
├ 📱 Username: @{user_data.get('username', 'Noma\'lum')}
├ 📅 Qo'shilgan: {user_data.get('join_date', 'Noma\'lum')}
└ 🔄 So'nggi faollik: {user_data.get('last_active', 'Noma\'lum')}

🎯 *Faoliyat ko'rsatkichlari:*
{create_progress_bar(referral_progress)} {referral_progress:.0f}%
├ 👥 Takliflar: *{user_data.get('referrals', 0)} ta*
├ 🎯 Ballar: *{user_data.get('points', 0)} ball*
├ 📈 Daraja: *{user_data.get('level', 1)}*
└ 🏆 Yutuqlar: *{len(user_data.get('achievements', []))} ta*

💰 *Moliyaviy ma'lumotlar:*
├ 🏦 Jami yutganlar: *{user_data.get('total_earned', 0):,} so'm*
├ 🎫 Qur'a holati: *{'✅ Kirgan' if user_data.get('referrals', 0) >= 10 else f'❌ {10 - user_data.get("referrals", 0)} ta yetmaydi'}*
├ ⚠️ Ogohlantirishlar: *{user_data.get('warnings', 0)} ta*
└ 📊 Daraja: *{user_data.get('rank', 'beginner').capitalize()}*

🏆 *Keyingi qur'a:* {bot.config['next_draw_date']}
"""
    
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
    
    rank_emojis = {
        'beginner': '👶',
        'pro': '⚡',
        'expert': '🌟',
        'master': '👑',
        'legend': '🔥'
    }
    
    ref_count = user_data.get('referrals', 0)
    
    profile_text = f"""
👤 *SHAXSIY PROFIL*

{rank_emojis.get(user_data.get('rank', 'beginner'), '👤')} *{user_data.get('full_name', query.from_user.first_name)}*

📊 *Asosiy ma'lumotlar:*
├ 🆔 ID: `{user_id}`
├ 📱 Username: @{user_data.get('username', 'Yo\'q')}
├ 📅 A'zo bo'lgan: {user_data.get('join_date', 'Noma\'lum')}
└ 🔄 Oxirgi faollik: {user_data.get('last_active', 'Noma\'lum')}

🏆 *Darajalar tizimi:*
├ {create_progress_bar(100 if ref_count >= 5 else (ref_count/5)*100)} 👶 Beginner (0-5)
├ {create_progress_bar(100 if ref_count >= 10 else max(0, (ref_count-5)/5)*100)} ⚡ Pro (5-10)
├ {create_progress_bar(100 if ref_count >= 25 else max(0, (ref_count-10)/15)*100)} 🌟 Expert (10-25)
├ {create_progress_bar(100 if ref_count >= 50 else max(0, (ref_count-25)/25)*100)} 👑 Master (25-50)
└ {create_progress_bar(100 if ref_count >= 100 else max(0, (ref_count-50)/50)*100)} 🔥 Legend (50+)

🎯 *Joriy daraja:* {user_data.get('rank', 'beginner').capitalize()} {rank_emojis.get(user_data.get('rank', 'beginner'), '👤')}

📈 *Statistikalar:*
├ 👥 Ko'rishlar: {user_data.get('profile_views', 0)} marta
├ 🔥 Streak: {user_data.get('daily_streak', 0)} kun
└ 🏆 Yutuqlar: {len(user_data.get('achievements', []))} ta
"""
    
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
    
    qualified = sum(1 for u in bot.data['users'].values() if u.get('referrals', 0) >= 10 and not u.get('banned', False))
    total_prizes = sum(p['amount'] for p in bot.config['prizes'])
    
    giveaway_text = f"""
👑 *PREMIUM QUR'A TIZIMI*

💰 *JACKPOT SOVG'ALARI:*
{prizes_text}

🎯 *Umumiy jamg'arma:* *{total_prizes:,} so'm*

📊 *Statistika:*
├ 👥 Jami ishtirokchilar: *{qualified} ta*
├ 📅 Keyingi qur'a: *{bot.config['next_draw_date']}*
├ 🎯 Minimal taklif: *{bot.config['min_referrals']} ta*
└ 💰 Bonus: *{bot.config['referral_bonus']} ball/taklif*

📋 *Qatnashish shartlari:*
1. @{CHANNEL_USERNAME} kanaliga haqiqiy a'zo bo'ling
2. *{bot.config['min_referrals']} ta* do'st taklif qiling
3. Har bir taklif uchun *{bot.config['referral_bonus']} ball* oling
4. Qur'a kuni tasodifiy g'oliblar tanlanadi

⚠️ *DIQQAT:* Faqat kanal a'zolari va {bot.config['min_referrals']}+ taklif to'plaganlar qatnasha oladi!

🎲 *G'oliblar:* Tasodifiy tanlanadi
"""
    
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
    
    invite_text = f"""
🚀 *TAKLIF QILISH TIZIMI*

🔗 *Shaxsiy havola:*
`{user_link}`

📊 *Statistika:*
{create_progress_bar(progress)} {progress:.0f}%
├ 👥 Joriy takliflar: *{referrals} ta*
├ 🎯 Kerakli takliflar: *{bot.config['min_referrals']} ta*
├ 📈 Qolgan: *{needed} ta*
└ 🎫 Holat: *{'✅ Qur\'aga kirdingiz!' if referrals >= bot.config['min_referrals'] else '⏳ Jarayonda...'}*

💰 *Bonus tizimi:*
├ 5️⃣ {create_progress_bar(100 if referrals >= 5 else (referrals/5)*100)} *5 ta = +50 ball*
├ 🔟 {create_progress_bar(100 if referrals >= 10 else (referrals/10)*100)} *10 ta = +100 ball*
├ 2️⃣5️⃣ {create_progress_bar(100 if referrals >= 25 else (referrals/25)*100)} *25 ta = +250 ball*
├ 5️⃣0️⃣ {create_progress_bar(100 if referrals >= 50 else (referrals/50)*100)} *50 ta = +500 ball*
└ 💯 {create_progress_bar(100 if referrals >= 100 else (referrals/100)*100)} *100 ta = +1000 ball*

💡 *Maslahat:* Havolani nusxalab, do'stlaringizga yuboring!
"""
    
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
    
    await query.answer(f"✅ Havola nusxalandi!\n\n{user_link}", show_alert=True)


async def leaderboard_panel(query, context):
    """🏆 Reyting paneli"""
    active_users = {uid: data for uid, data in bot.data['users'].items() if not data.get('banned', False)}
    
    top_users = sorted(
        active_users.items(),
        key=lambda x: x[1].get('referrals', 0),
        reverse=True
    )[:10]
    
    text = "🏆 *TOP 10 FOYDALANUVCHI*\n\n"
    
    for i, (uid, data) in enumerate(top_users, 1):
        emoji = "👑" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        name = data.get('full_name', 'Noma\'lum')[:12]
        referrals = data.get('referrals', 0)
        points = data.get('points', 0)
        
        rank_emoji = {
            'beginner': '👶', 'pro': '⚡', 'expert': '🌟', 
            'master': '👑', 'legend': '🔥'
        }.get(data.get('rank', 'beginner'), '👤')
        
        text += f"{emoji} *{name}* {rank_emoji}\n"
        text += f"   👥 {referrals} ta | 🎯 {points} ball\n\n"
    
    user_id = str(query.from_user.id)
    user_rank = 0
    user_referrals = active_users.get(user_id, {}).get('referrals', 0)
    
    all_users = sorted(active_users.items(), key=lambda x: x[1].get('referrals', 0), reverse=True)
    
    for i, (uid, _) in enumerate(all_users, 1):
        if uid == user_id:
            user_rank = i
            break
    
    if user_rank == 0:
        text += f"\n📊 *Siz hali ro'yxatda emassiz*"
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
    help_text = f"""
❓ *YORDAM VA QO'LLANMA*

🤖 *Bot haqida:*
Bu premium qur'a boti bo'lib, do'stlaringizni taklif qilib katta sovg'alarni yutib olishingiz mumkin.

💰 *Sovg'alar:*
• 👑 1-o'rin: 30,000,000 so'm
• 🥈 2-o'rin: 15,000,000 so'm  
• 🥉 3-o'rin: 8,000,000 so'm

📋 *Qo'llanma:*
1. Kanalga a'zo bo'ling (@{CHANNEL_USERNAME})
2. Do'stlaringizni taklif qiling
3. *{bot.config['min_referrals']}+* taklif to'plang
4. Qur'a kuni g'olib bo'ling

⚠️ *Qoidalar:*
• Faqat haqiqiy kanal a'zolari qatnasha oladi
• Soxta takliflar bloklanishiga olib keladi
• Har bir foydalanuvchi 1 ta akkaunt ocha oladi

🏆 *Darajalar:*
👶 Beginner (0-5)
⚡ Pro (5-10)
🌟 Expert (10-25)
👑 Master (25-50)
🔥 Legend (50+)

📞 *Kanal:* @{CHANNEL_USERNAME}
"""
    
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
        bonus_text = f"""
🎁 *KUNLIK BONUS*

⚠️ *Siz bugun bonus olgansiz!*

⏰ *Keyingi bonus:* Ertaga 00:00
🔥 *Streak:* {user_data.get('daily_streak', 0)} kun

💡 *Maslahat:* Ertaga kelib bonus oling!
"""
    else:
        streak = user_data.get('daily_streak', 0) + 1
        bonus = min(100, streak * 10)
        
        user_data['points'] = user_data.get('points', 0) + bonus
        user_data['last_daily'] = today
        user_data['daily_streak'] = streak
        bot.save_data()
        
        bonus_text = f"""
🎁 *KUNLIK BONUS OLINDI!*

💰 *Bonus:* +{bonus} ball
🔥 *Streak:* {streak} kun
🎯 *Jami:* {user_data['points']} ball

⏰ *Keyingi bonus:* Ertaga 00:00
"""
    
    keyboard = [
        [
            InlineKeyboardButton("📊 Statistika", callback_data='stats'),
            InlineKeyboardButton("👥 Taklif", callback_data='invite')
        ],
        [InlineKeyboardButton("🔙 Orqaga", callback_data='back')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(bonus_text, reply_markup=reply_markup, parse_mode='Markdown')
# 👑 ADMIN FUNKSIYALARI

async def admin_dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """👑 Admin dashboard"""
    if update.callback_query:
        query = update.callback_query
        user = query.from_user
        is_callback = True
    else:
        user = update.effective_user
        is_callback = False
    
    stats = bot.data['statistics']
    total_users = stats['total_users']
    active_users = sum(1 for u in bot.data['users'].values() if not u.get('banned', False))
    qualified_users = sum(1 for u in bot.data['users'].values() if u.get('referrals', 0) >= 10 and not u.get('banned', False))
    today_users = len([u for u in bot.data['users'].values() if datetime.now().strftime("%Y-%m-%d") in u.get('join_date', '')])
    
    dashboard_text = f"""
👑 *ADMIN DASHBOARD*
👤 Admin: *{user.full_name}*
🆔 ID: `{user.id}`

📈 *ASOSIY KO'RSATKICHLAR*
┌ 📊 Jami: *{total_users} ta*
├ ⚡ Faol: *{active_users} ta*
├ 🎯 Ishtirokchilar: *{qualified_users} ta*
└ 📅 Bugun: *{today_users} ta*

💰 *MOLIYAVIY*
┌ 🏦 Jami sovg'alar: *{stats['total_prizes']:,} so'm*
├ 🏆 G'oliblar: *{stats['total_winners']} ta*
└ 📊 Takliflar: *{stats['total_referrals']} ta*

⚙️ *SOZLAMALAR*
┌ 🔒 Kanal: *{'✅ Qattiq' if bot.config['strict_channel_check'] else '⚠️ Oddiy'}*
├ 🎯 Min taklif: *{bot.config['min_referrals']} ta*
└ 🎲 Qur'a: *{'✅ Faol' if bot.config['giveaway_active'] else '❌ Nofaol'}*

📅 *Keyingi qur'a:* {bot.config['next_draw_date']}
"""
    
    keyboard = [
        [
            InlineKeyboardButton("📊 STATISTIKA", callback_data='admin_stats'),
            InlineKeyboardButton("👑 QUR'A", callback_data='admin_draw')
        ],
        [
            InlineKeyboardButton("👥 USERLAR", callback_data='admin_users'),
            InlineKeyboardButton("⚙️ SOZLAMALAR", callback_data='admin_settings')
        ],
        [
            InlineKeyboardButton("📢 BROADCAST", callback_data='admin_broadcast'),
            InlineKeyboardButton("🔧 BOSHQARUV", callback_data='admin_management')
        ],
        [InlineKeyboardButton("📱 USER MENYU", callback_data='user_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if is_callback:
        await query.edit_message_text(dashboard_text, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.message.reply_text(dashboard_text, reply_markup=reply_markup, parse_mode='Markdown')


async def admin_stats_command(query, context):
    """📊 Admin statistika"""
    stats = bot.data['statistics']
    active_today = len([u for u in bot.data['users'].values() if datetime.now().strftime("%Y-%m-%d") in u.get('last_active', '')])
    
    admin_stats = f"""
📈 *TO'LIQ STATISTIKA*

👥 *FOYDALANUVCHILAR:*
├ 📊 Jami: *{stats['total_users']} ta*
├ ✅ Faol: *{sum(1 for u in bot.data['users'].values() if not u.get('banned', False))} ta*
├ ❌ Bloklangan: *{sum(1 for u in bot.data['users'].values() if u.get('banned', False))} ta*
└ 🔥 Bugun faol: *{active_today} ta*

🎯 *TAKLIFLAR:*
├ 📈 Jami: *{stats['total_referrals']} ta*
├ ⭐ Eng ko'p: *{max((u.get('referrals', 0) for u in bot.data['users'].values()), default=0)} ta*
└ 📊 O'rtacha: *{stats['total_referrals']/max(1, stats['total_users']):.1f} ta*

🏆 *QUR'A:*
├ 🎊 G'oliblar: *{stats['total_winners']} ta*
├ 💰 Sovg'alar: *{stats['total_prizes']:,} so'm*
├ 📅 So'nggi: *{stats['last_draw'] or 'Yo\'q'}*
└ 🎫 Ishtirokchilar: *{sum(1 for u in bot.data['users'].values() if u.get('referrals', 0) >= 10 and not u.get('banned', False))} ta*
"""
    
    keyboard = [[InlineKeyboardButton("🔙 Admin panel", callback_data='admin_dashboard')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.edit_text(admin_stats, reply_markup=reply_markup, parse_mode='Markdown')


async def admin_draw_panel(query, context):
    """🎲 Qur'a paneli"""
    qualified = [(uid, data) for uid, data in bot.data['users'].items() 
                if data.get('referrals', 0) >= 10 and not data.get('banned', False)]
    
    text = f"""
🎲 *QUR'A PANELI*

📊 *ISHTIROKCHILAR:* *{len(qualified)} ta*
📅 *KEYINGI:* *{bot.config['next_draw_date']}*

💰 *SOVG'ALAR:*
"""
    for prize in bot.config['prizes']:
        text += f"{prize['emoji']} {prize['place']}-o'rin: *{prize['amount']:,} so'm*\n"
    
    text += f"\n⚡ *Holat:* *{'✅ Tayyor' if len(qualified) >= 3 else '❌ Yetarli emas'}*"
    
    keyboard = []
    if len(qualified) >= 3:
        keyboard.append([InlineKeyboardButton("🎲 QUR'A O'TKAZISH", callback_data='execute_draw')])
    keyboard.append([InlineKeyboardButton("🔙 Admin panel", callback_data='admin_dashboard')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode='Markdown')


async def execute_draw_from_callback(query, context):
    """🎲 Callback dan qur'a o'tkazish"""
    user = query.from_user
    
    if user.id not in bot.config['admin_ids']:
        await query.answer("❌ Faqat admin uchun!", show_alert=True)
        return
    
    qualified = [(uid, data) for uid, data in bot.data['users'].items() 
                if data.get('referrals', 0) >= bot.config['min_referrals'] and not data.get('banned', False)]
    
    if len(qualified) < 3:
        await query.answer(f"⚠️ Yetarli emas! ({len(qualified)}/3)", show_alert=True)
        return
    
    await query.answer("🎲 Qur'a boshlanmoqda...", show_alert=True)
    
    random.seed(datetime.now().timestamp())
    winners = random.sample(qualified, min(3, len(qualified)))
    
    result = f"""
🎊 *QUR'A NATIJALARI* 🎊

📅 *Sana:* {datetime.now().strftime('%Y-%m-%d %H:%M')}
👥 *Ishtirokchilar:* {len(qualified)} ta

🏆 *G'OLIBLAR:*

"""
    
    total_prizes = 0
    for i, (winner_id, winner_data) in enumerate(winners, 1):
        prize = bot.config['prizes'][i-1]
        total_prizes += prize['amount']
        
        result += f"""{prize['emoji']} *{i}-o'rin:*
   👤 {winner_data.get('full_name', 'N/A')}
   💰 {prize['amount']:,} so'm
   🆔 `{winner_id}`

"""
        
        bot.data['users'][winner_id]['total_earned'] = bot.data['users'][winner_id].get('total_earned', 0) + prize['amount']
        bot.data['users'][winner_id]['points'] = bot.data['users'][winner_id].get('points', 0) + 1000
        
        if f'winner_{i}' not in bot.data['users'][winner_id].get('achievements', []):
            bot.data['users'][winner_id].setdefault('achievements', []).append(f'winner_{i}')
    
    bot.config['next_draw_date'] = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    bot.data['statistics']['last_draw'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    bot.data['statistics']['total_winners'] += 3
    bot.data['statistics']['total_prizes'] += total_prizes
    
    bot.save_data()
    bot.save_config()
    
    # G'oliblarga xabar
    for i, (winner_id, winner_data) in enumerate(winners, 1):
        prize = bot.config['prizes'][i-1]
        try:
            congrat_msg = f"""
🎉 *TABRIKLAYMIZ! SIZ G'OLIB!*

🏆 *O'rin:* {i}-o'rin
💰 *Mukofot:* {prize['amount']:,} so'm
🎯 *Takliflar:* {winner_data.get('referrals', 0)} ta

📞 *Admin bilan bog'laning*
🆔 *ID:* `{winner_id}`
"""
            await context.bot.send_message(chat_id=int(winner_id), text=congrat_msg, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"❌ G'olibga xabar: {e}")
    
    await query.edit_message_text(result, parse_mode='Markdown')


async def admin_users_panel(query, context):
    """👥 Foydalanuvchilar"""
    total = len(bot.data['users'])
    active = sum(1 for u in bot.data['users'].values() if not u.get('banned', False))
    banned = sum(1 for u in bot.data['users'].values() if u.get('banned', False))
    
    top_users = sorted([(uid, data) for uid, data in bot.data['users'].items() if not data.get('banned', False)],
                      key=lambda x: x[1].get('referrals', 0), reverse=True)[:5]
    
    text = f"""
👥 *FOYDALANUVCHILAR*

📊 *UMUMIY:*
├ 👥 Jami: *{total} ta*
├ ✅ Faol: *{active} ta*
└ ❌ Bloklangan: *{banned} ta*

🏆 *TOP 5:*
"""
    for i, (uid, data) in enumerate(top_users, 1):
        text += f"{i}. *{data.get('full_name', 'N/A')[:15]}* - {data.get('referrals', 0)} ta\n"
    
    keyboard = [[InlineKeyboardButton("🔙 Admin panel", callback_data='admin_dashboard')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode='Markdown')


async def admin_settings_panel(query, context):
    """⚙️ Sozlamalar"""
    text = f"""
⚙️ *SOZLAMALAR*

🔒 *Kanal:* {'✅ Qattiq' if bot.config['strict_channel_check'] else '⚠️ Oddiy'}
🎯 *Min taklif:* {bot.config['min_referrals']} ta
💰 *Bonus:* {bot.config['referral_bonus']} ball
🎲 *Qur'a:* {'✅ Faol' if bot.config['giveaway_active'] else '❌ Nofaol'}
📅 *Keyingi:* {bot.config['next_draw_date']}

⚡ *Bonuslar:*
"""
    for i in range(len(bot.config['bonus_referrals'])):
        text += f"├ {bot.config['bonus_referrals'][i]} ta = +{bot.config['bonus_points'][i]} ball\n"
    
    keyboard = [[InlineKeyboardButton("🔙 Admin panel", callback_data='admin_dashboard')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode='Markdown')


async def admin_broadcast_panel(query, context):
    """📢 Broadcast"""
    text = """
📢 *BROADCAST*

Xabar yuborish:
`/broadcast <xabar>`

*Misol:*
`/broadcast Yangi qur'a!`

⚠️ Barcha faol userlarga yuboriladi.
"""
    
    keyboard = [[InlineKeyboardButton("🔙 Admin panel", callback_data='admin_dashboard')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode='Markdown')


async def admin_management_panel(query, context):
    """🔧 Boshqaruv"""
    text = """
🔧 *BOSHQARUV PANELI*

*Buyruqlar:*

👤 *User:*
• `/user <id>` - Ma'lumot
• `/ban <id> <sabab>` - Bloklash
• `/unban <id>` - Ochish

📊 *Statistika:*
• `/stats` - To'liq

🎲 *Qur'a:*
• `/draw` - O'tkazish

📢 *Broadcast:*
• `/broadcast <xabar>`
"""
    
    keyboard = [[InlineKeyboardButton("🔙 Admin panel", callback_data='admin_dashboard')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode='Markdown')


# 🔧 ADMIN COMMANDS

async def admin_draw_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🎲 Qur'a command"""
    user = update.effective_user
    
    if user.id not in bot.config['admin_ids']:
        await update.message.reply_text("❌ *Faqat admin!*", parse_mode='Markdown')
        return
    
    qualified = [(uid, data) for uid, data in bot.data['users'].items() 
                if data.get('referrals', 0) >= bot.config['min_referrals'] and not data.get('banned', False)]
    
    if len(qualified) < 3:
        await update.message.reply_text(f"⚠️ *Yetarli emas!*\nJami: {len(qualified)}/3", parse_mode='Markdown')
        return
    
    await update.message.reply_text("🎲 *Qur'a boshlanmoqda...*", parse_mode='Markdown')
    
    random.seed(datetime.now().timestamp())
    winners = random.sample(qualified, 3)
    
    result = f"🎊 *QUR'A NATIJALARI*\n\n"
    
    for i, (winner_id, winner_data) in enumerate(winners, 1):
        prize = bot.config['prizes'][i-1]
        result += f"{prize['emoji']} {i}. {winner_data.get('full_name', 'N/A')}\n💰 {prize['amount']:,} so'm\n\n"
        
        bot.data['users'][winner_id]['total_earned'] = bot.data['users'][winner_id].get('total_earned', 0) + prize['amount']
        
        try:
            await context.bot.send_message(
                chat_id=int(winner_id),
                text=f"🎉 *TABRIK! {i}-o'rin!*\n💰 {prize['amount']:,} so'm",
                parse_mode='Markdown'
            )
        except:
            pass
    
    bot.config['next_draw_date'] = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    bot.data['statistics']['total_winners'] += 3
    bot.save_data()
    bot.save_config()
    
    await update.message.reply_text(result, parse_mode='Markdown')


async def admin_broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """📢 Broadcast command"""
    user = update.effective_user
    
    if user.id not in bot.config['admin_ids']:
        await update.message.reply_text("❌ *Faqat admin!*", parse_mode='Markdown')
        return
    
    if not context.args:
        await update.message.reply_text("📝 *Foydalanish:* /broadcast <xabar>", parse_mode='Markdown')
        return
    
    message_text = ' '.join(context.args)
    users = [uid for uid, data in bot.data['users'].items() 
            if data.get('notifications', True) and not data.get('banned', False)]
    
    sent = 0
    failed = 0
    
    progress = await update.message.reply_text(f"📤 *Yuborilmoqda... 0/{len(users)}*", parse_mode='Markdown')
    
    for i, user_id in enumerate(users, 1):
        try:
            await context.bot.send_message(
                chat_id=int(user_id),
                text=f"📢 *XABAR*\n\n{message_text}\n\n— Admin",
                parse_mode='Markdown'
            )
            sent += 1
        except:
            failed += 1
        
        if i % 10 == 0:
            await progress.edit_text(f"📤 *Yuborilmoqda... {i}/{len(users)}*", parse_mode='Markdown')
        
        await asyncio.sleep(0.1)
    
    await progress.edit_text(
        f"✅ *Yuborildi!*\n\n"
        f"📤 *Muvaffaqiyatli:* {sent} ta\n"
        f"❌ *Xato:* {failed} ta\n"
        f"👥 *Jami:* {len(users)} ta",
        parse_mode='Markdown'
    )


async def admin_user_info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """👤 User info command"""
    user = update.effective_user
    
    if user.id not in bot.config['admin_ids']:
        await update.message.reply_text("❌ *Faqat admin!*", parse_mode='Markdown')
        return
    
    if not context.args:
        await update.message.reply_text("👤 *Foydalanish:* /user <id>", parse_mode='Markdown')
        return
    
    target_id = context.args[0]
    
    if target_id not in bot.data['users']:
        await update.message.reply_text("❌ *User topilmadi!*", parse_mode='Markdown')
        return
    
    user_data = bot.data['users'][target_id]
    
    user_info = f"""
👤 *USER MA'LUMOTLARI*

🆔 *ID:* `{target_id}`
👤 *Ism:* {user_data.get('full_name', 'N/A')}
📱 *Username:* @{user_data.get('username', 'N/A')}

📊 *STATISTIKA:*
├ 👥 Takliflar: *{user_data.get('referrals', 0)} ta*
├ 🎯 Ballar: *{user_data.get('points', 0)} ball*
├ 💰 Yutgan: *{user_data.get('total_earned', 0):,} so'm*
└ 🔓 Holat: *{'✅ Faol' if not user_data.get('banned', False) else '❌ Bloklangan'}*
"""
    
    await update.message.reply_text(user_info, parse_mode='Markdown')


async def admin_ban_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🚫 Ban command"""
    user = update.effective_user
    
    if user.id not in bot.config['admin_ids']:
        await update.message.reply_text("❌ *Faqat admin!*", parse_mode='Markdown')
        return
    
    if len(context.args) < 2:
        await update.message.reply_text("🚫 *Foydalanish:* /ban <id> <sabab>", parse_mode='Markdown')
        return
    
    target_id = context.args[0]
    reason = ' '.join(context.args[1:])
    
    if target_id not in bot.data['users']:
        await update.message.reply_text("❌ *User topilmadi!*", parse_mode='Markdown')
        return
    
    bot.data['users'][target_id]['banned'] = True
    bot.save_data()
    
    try:
        await context.bot.send_message(
            chat_id=int(target_id),
            text=f"🚫 *BLOKLANDI!*\n\nℹ️ *Sabab:* {reason}",
            parse_mode='Markdown'
        )
    except:
        pass
    
    await update.message.reply_text(f"✅ *User bloklandi!*\n*Sabab:* {reason}", parse_mode='Markdown')


async def admin_unban_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """✅ Unban command"""
    user = update.effective_user
    
    if user.id not in bot.config['admin_ids']:
        await update.message.reply_text("❌ *Faqat admin!*", parse_mode='Markdown')
        return
    
    if not context.args:
        await update.message.reply_text("✅ *Foydalanish:* /unban <id>", parse_mode='Markdown')
        return
    
    target_id = context.args[0]
    
    if target_id not in bot.data['users']:
        await update.message.reply_text("❌ *User topilmadi!*", parse_mode='Markdown')
        return
    
    bot.data['users'][target_id]['banned'] = False
    bot.save_data()
    
    try:
        await context.bot.send_message(
            chat_id=int(target_id),
            text="✅ *AKKAUNT FAOLLASHTIRILDI!*\n\nEndi botdan foydalanishingiz mumkin.",
            parse_mode='Markdown'
        )
    except:
        pass
    
    await update.message.reply_text(f"✅ *User faollashtirildi!*", parse_mode='Markdown')


async def admin_stats_full_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """📈 Stats command"""
    user = update.effective_user
    
    if user.id not in bot.config['admin_ids']:
        await update.message.reply_text("❌ *Faqat admin!*", parse_mode='Markdown')
        return
    
    stats = bot.data['statistics']
    
    full_stats = f"""
📈 *TO'LIQ STATISTIKA*

👥 *USERLAR:* {stats['total_users']} ta
🎯 *TAKLIFLAR:* {stats['total_referrals']} ta
🏆 *G'OLIBLAR:* {stats['total_winners']} ta
💰 *SOVG'ALAR:* {stats['total_prizes']:,} so'm

📊 *So'nggi qur'a:* {stats['last_draw'] or 'Yo\'q'}
"""
    
    await update.message.reply_text(full_stats, parse_mode='Markdown')


# 🏃‍♂️ MAIN FUNCTION

def main():
    """🚀 Main"""
    TOKEN = "8366431363:AAEdZ2uX0dC6LflUhx8sgyciPuSJMHzL4d4"
    
    application = Application.builder().token(TOKEN).build()
    
    # User commands
    application.add_handler(CommandHandler("start", start))
    
    # Admin commands
    application.add_handler(CommandHandler("draw", admin_draw_command))
    application.add_handler(CommandHandler("broadcast", admin_broadcast_command))
    application.add_handler(CommandHandler("user", admin_user_info_command))
    application.add_handler(CommandHandler("ban", admin_ban_user_command))
    application.add_handler(CommandHandler("unban", admin_unban_user_command))
    application.add_handler(CommandHandler("stats", admin_stats_full_command))
    
    # Callback handler
    application.add_handler(CallbackQueryHandler(button_handler))
    
    print("\n" + "="*60)
    print("🎁 PREMIUM GIVEAWAY BOT ISHGA TUSHDI 🎁")
    print("="*60)
    print(f"📊 Userlar: {bot.data['statistics']['total_users']} ta")
    print(f"🎯 Takliflar: {bot.data['statistics']['total_referrals']} ta")
    print(f"💰 Sovg'alar: {bot.data['statistics']['total_prizes']:,} so'm")
    print(f"🏆 G'oliblar: {bot.data['statistics']['total_winners']} ta")
    print(f"👑 Admin: {bot.config['admin_ids'][0]}")
    print(f"📅 Keyingi qur'a: {bot.config['next_draw_date']}")
    print("="*60 + "\n")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
