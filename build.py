"""Builds every page of the Discord for School tutorial.
Run: python3 build.py

Each section and each subsection is its own page. The left sidebar
(Table of Contents) is generated from SECTIONS so it is identical on every page.
New words use T('key') and show their definition on hover or keyboard focus.
Media placeholders use media('note for Sebastian') and render as blank boxes.
"""
import html, os, re, glob

SITE = 'Discord for School'
TITLE = "Discord for College: Desktop App Version"

# ---------------------------------------------------------------------------
# New words (blue text + hover definition). Also used to build the Glossary.
# ---------------------------------------------------------------------------
DEF = {
    'desktop app': 'The version of Discord you download and install on a Windows PC.',
    'server': 'A private space on Discord for one group, class, or club. Each server has its own channels and members.',
    'channel': 'A separate area inside a server for one topic or activity. A server can have many channels.',
    'text channel': 'A channel marked with a pound sign (#) where people type messages and share files.',
    'voice channel': 'A channel marked with a speaker icon where people talk live with their voice, camera, or screen.',
    'username': 'Your unique account name. No two Discord accounts can have the same username.',
    'display name': 'The name other people see next to your messages. It does not have to be unique.',
    'CAPTCHA': 'A short puzzle, such as a checkbox or picture question, that proves you are a person and not a program.',
    'avatar': 'Your profile picture. It appears next to every message you send.',
    'User Settings': 'The menu where you change your account, profile, language, and text size. Open it with the gear icon at the bottom left.',
    'invite link': 'A web address, usually starting with discord.gg/, that lets you join a specific server.',
    'server nickname': 'A name you use in only one server. It replaces your display name in that server and nowhere else.',
    'member list': 'The column on the right side of a server that shows who belongs to the server and who is online.',
    'server list': 'The column of round icons on the far left of Discord. Each icon is a server you belong to.',
    'channel list': 'The column next to the server list that shows every channel in the server you selected.',
    'chat area': 'The large center area of Discord that shows the messages in the channel you selected.',
    'user panel': 'The small bar at the bottom left of Discord with your name, your microphone button, your headphone button, and the gear icon.',
    'mute': 'To turn off your microphone so no one can hear you. You can still hear others.',
    'deafen': 'To turn off all sound coming into Discord. Deafening also mutes your microphone.',
    'category': 'A heading in the channel list that groups related channels, such as TEXT CHANNELS or VOICE CHANNELS.',
    'reply': 'A message that is attached to an earlier message so everyone can see what you are answering.',
    'reaction': 'A small emoji added under a message. Groups often use reactions to say "I saw this" or to vote.',
    'direct message': 'A private conversation between you and one person or a small group, outside of any server. Often shortened to DM.',
    'thread': 'A side conversation attached to one message in a channel, so a long discussion does not crowd the main channel.',
    'mention': 'Typing the @ symbol followed by a name so that person receives a notification. Also called a ping.',
    'role': 'A label a server gives to a group of members, such as @Presenters. Roles can control who sees certain channels.',
    'moderator': 'A server member who manages channels, roles, and members, and keeps the server organized.',
    'unread indicator': 'A white dot or bold channel name that shows there are new messages you have not read.',
    'mention badge': 'A red circle with a number that shows how many times someone mentioned you.',
    'Inbox': 'The tray icon at the top right of Discord that collects your recent mentions and unread messages in one list.',
    'pinned message': 'An important message that a group saves to a channel\'s pinned list so it is easy to find later.',
    'attachment': 'A file, such as a document, slide deck, or image, that you add to a message.',
    'Do Not Disturb': 'A status that turns off all desktop notifications and notification sounds until you change it back. It shows as a red circle on your picture.',
    'block': 'To stop a person from sending you direct messages and to hide their messages in servers you share.',
    'two-factor authentication': 'A login protection that asks for a code from your phone in addition to your password. Often shortened to 2FA.',
    'backup codes': 'One-time codes that let you log in if you lose the phone you use for two-factor authentication.',
    'voice status panel': 'The bar that appears above your user panel while you are in a voice channel. It shows Voice Connected and has the Disconnect, Video, and Share Your Screen buttons.',
    'screen share': 'Showing a window or your whole screen to the people in a voice channel. Discord calls this Go Live.',
}

ICON = {
    'note': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>',
    'caution': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/><path d="M12 9v4"/><path d="M12 17h.01"/></svg>',
    'menu': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M3 6h18M3 12h18M3 18h18"/></svg>',
}

LOGO = '<img src="media/discord-logo.png" alt="" width="36" height="36">'


def T(key, shown=None):
    """A new word: blue text, definition on hover/focus."""
    d = html.escape(DEF[key], quote=True)
    return f'<span class="term" tabindex="0" data-def="{d}">{shown or key}</span>'


def note(h):
    return (f'<aside class="callout note" role="note" aria-label="Note">{ICON["note"]}'
            f'<p><span class="label">Note</span>{h}</p></aside>')


def caution(h):
    return (f'<aside class="callout caution" role="note" aria-label="Caution">{ICON["caution"]}'
            f'<p><span class="label">Caution</span>{h}</p></aside>')


def media(todo, small=False):
    """Marks a media spot. Each marker is numbered by page and position (for example 2.3.1)
    when the page is written. A matching file in media/ is shown; otherwise a placeholder."""
    return f'@@MEDIA[{html.escape(todo, quote=True)}]@@'


# Alt text for media that is ready, keyed by label (subsection number + position)
MEDIA = {
    '1.2.1': 'This tutorial open in a web browser',
    '1.2.2': 'The web browser moved to the left half of the screen',
    '1.2.3': 'Opening the Discord app from the taskbar',
    '1.2.4': 'This tutorial open in a web browser on the left half of the screen and Discord open on the right half',
    '2.1.1': 'Typing discord.com/download into the web browser address bar',
    '2.1.2': 'The Download for Windows button on the Discord download page',
    '2.1.3': 'The DiscordSetup.exe file in the Downloads folder',
    '2.1.4': 'The Discord installer window while the app installs',
    '2.2.1': 'The Discord app icon on the Windows desktop',
    '2.2.2': 'The Register link under the Log In button on the login screen',
    '2.2.3': 'The Email box on the Create an account form',
    '2.2.4': 'The Display Name box on the Create an account form',
    '2.2.5': 'The Username box on the Create an account form',
    '2.2.6': 'The Password box on the Create an account form',
    '2.2.7': 'The month, day, and year menus for your date of birth',
    '2.2.8': 'The button at the bottom of the Create an account form',
    '2.2.9': 'The CAPTCHA box next to I am human',
    '2.2.10': 'The Discord home screen after signing up, with a green bar at the top asking you to verify your email',
    '2.2.11': 'Opening the email inbox',
    '2.2.12': 'The email from Discord with the subject Verify Email Address for Discord',
    '2.2.13': 'The Verify Email button inside the email from Discord',
    '2.3.1': 'Your name in the user panel at the bottom-left corner of the Discord window',
    '2.3.2': 'The gear icon (User Settings) to the right of your name',
    '2.3.3': 'The Edit Profiles link in User Settings',
    '2.3.4': 'The Change Avatar option after clicking your avatar',
    '2.3.5': 'The Upload Image option',
    '2.3.6': 'Choosing a picture in the Open window',
    '2.3.7': 'Adjusting the crop of the picture with the slider',
    '2.3.8': 'The Apply button under the crop window',
    '2.3.9': 'The Save button in the bar at the bottom of the window',
    '2.3.10': 'The Add pronouns area next to your username',
    '2.3.11': 'Typing your pronouns, such as He/Him',
    '2.3.12': 'The Save button after adding pronouns',
    '2.3.13': 'Language & Time in the User Settings list',
    '2.3.14': 'Choosing Español, LATAM in the language list',
    '2.3.15': 'Accessibility in the User Settings list',
    '2.3.16': 'Text size in chat under Text Readability',
    '2.3.17': 'Dragging the Text size in chat slider to the right',
    '3.1.1': 'A server with its channel list on the left and its member list on the right',
    '3.1.2': 'The round server icons in the column on the far left',
    '3.2.1': 'The user panel at the bottom-left, which shows you are logged in',
    '3.2.2': 'The Join button on an invite link',
    '3.2.3': 'An invite link in a message',
    '3.2.4': 'The plus button (Add a Server) in the server column',
    '3.2.5': 'The Join a Server button at the bottom of the Create Your Server window',
    '3.2.6': 'Pasting the link into the Invite Link box',
    '3.2.7': 'The Join Server button',
    '3.3.1': 'Your profile (the cat avatar) in the member list on the right side of the server',
    '3.3.2': 'The Edit Profile button and the Edit Per-server Profile option',
    '3.3.3': 'The nickname under your avatar on your per-server profile',
    '3.3.4': 'The Save button at the bottom of the window',
    '4.1.1': 'The server list on the far left',
    '4.1.2': 'The channel list',
    '4.1.3': 'The chat area in the center',
    '4.1.4': 'The member list on the right',
    '4.1.5': 'The member list icon (two people) at the top-right of the window',
    '4.2.1': 'A text channel with a pound sign (#) before its name',
    '4.2.2': 'A voice channel with a speaker icon before its name',
    '4.3.1': 'The user panel at the bottom-left of the Discord window',
    '4.3.2': 'The Mute (microphone) and Deafen (headphone) buttons in the user panel',
    '5.1.1': 'Clicking a text channel in the channel list',
    '5.1.2': 'The message box at the bottom of the chat area',
    '5.1.3': 'Typing a message in the message box',
    '5.1.4': 'The sent message in the chat area',
    '5.1.5': 'Holding the pointer over your message',
    '5.1.6': 'The pencil icon (Edit) on the right of the message',
    '5.1.7': 'Changing the text of the message',
    '5.1.8': 'The edited message after pressing Enter',
    '5.1.9': 'Holding the pointer over the message you want to answer',
    '5.1.10': 'The Reply arrow on the right of the message',
    '5.1.11': 'Typing an answer in the reply box',
    '5.1.12': 'The reply in the chat area',
    '5.1.13': 'Holding the pointer over the message',
    '5.1.14': 'The smiley face icon (Add Reaction)',
    '5.1.15': 'Choosing the thumbs up emoji',
    '5.1.16': 'The thumbs up reaction under the message',
    '5.1.17': "Clicking a teammate's name in the member list",
    '5.1.18': "Typing in the Message @ box on the teammate's profile card",
    '5.1.19': 'The direct message after pressing Enter',
    '5.1.20': 'Holding the pointer over the message you want to discuss',
    '5.1.21': 'The three dots (More) on the right of the message',
    '5.1.22': 'Create Thread in the More menu',
    '5.1.23': 'Typing a name for the thread',
    '5.1.24': 'Typing the first message of the thread',
    '5.1.25': 'The thread after pressing Enter',
    '5.2.1': 'Typing the @ symbol in the message box',
    '5.2.2': "Typing the first few letters of a teammate's name after the @ symbol",
    '5.2.3': "The teammate's name in the list above the message box",
    '5.2.4': 'Finishing the message in the message box',
    '5.2.5': 'The message with the mention after pressing Enter',
    '5.3.1': 'The tray icon (Inbox) at the top-right of the Discord window',
    '5.3.2': 'The Mentions tab in the Inbox',
    '5.3.3': 'The jump icon next to a mention in the Inbox',
    '5.3.4': 'Opening a channel from the channel list',
    '5.3.5': 'The pin icon at the top-right of the window',
    '5.3.6': 'The Jump button next to a pinned message',
    '5.3.7': 'The Search box at the top-right of the window',
    '5.3.8': 'Typing deadline in the Search box',
    '5.3.9': 'The search results after pressing Enter',
    '5.3.10': 'Clicking a search result to jump to the message',
    '5.4.1': 'Opening the #files-and-drafts channel',
    '5.4.2': 'The plus button on the left side of the message box',
    '5.4.3': 'Upload a File in the plus button menu',
    '5.4.4': 'Choosing a file in the Open window',
    '5.4.5': 'The Open button in the Open window',
    '5.4.6': 'Typing a short message that explains the file',
    '5.4.7': 'The message and file in the channel after pressing Enter',
    '5.4.8': 'The Search box at the top-right of the window',
    '5.4.9': 'Typing has: in the Search box',
    '5.4.10': 'The has: file filter in the Search box after clicking file in the list',
    '5.4.11': 'The search result with the message that includes the file after pressing Enter',
    '6.1.1': 'Right-clicking the server icon in the server list',
    '6.1.2': 'Notification Settings in the server menu',
    '6.1.3': 'Only @mentions selected under Notification Settings',
    '6.1.4': 'The Suppress @everyone and @here switch turned on',
    '6.1.5': 'Right-clicking the server icon in the server list',
    '6.1.6': 'Pointing to Mute Server in the server menu',
    '6.1.7': 'For 1 Hour in the Mute Server menu',
    '6.1.8': 'Your picture in the user panel at the bottom-left of the window',
    '6.1.9': 'Your current status, Online, in the profile menu',
    '6.1.10': 'Pointing to Do Not Disturb in the status menu',
    '6.1.11': 'For 1 Hour in the Do Not Disturb menu',
    '6.2.1': 'The gear icon (User Settings) in the user panel',
    '6.2.2': 'Messaging Permissions in the list on the left of User Settings',
    '6.2.3': 'The All servers menu under Direct Message (DM) Permissions',
    '6.2.4': 'The Direct Messages switch under Direct Message (DM) Permissions',
    '6.2.5': 'The Yes button in the Server Privacy window',
    '6.2.6': 'Friend Request Permissions in Messaging Permissions',
    '6.2.7': 'The Everyone switch turned off under Allow Friend Requests from',
    '6.2.8': 'The Server members switch turned off under Allow Friend Requests from',
    '6.2.9': "Right-clicking a person's name in the Direct Messages list",
    '6.2.10': 'Block in the right-click menu',
    '6.2.11': 'The Block button in the Block window',
    '6.2.12': 'Right-clicking the message you want to report',
    '6.2.13': 'Report Message in the right-click menu',
    '6.2.14': 'The list of reasons in the report window',
    '6.2.15': 'The follow-up options in the report window',
    '6.2.16': "Google Authenticator installed from the phone's app store",
    '6.2.17': 'The gear icon (User Settings) in the user panel',
    '6.2.18': 'Account in the list on the left of User Settings',
    '6.2.19': 'Password & Security under Account in the list on the left',
    '6.2.20': 'The Enable Authenticator App button under Multi-Factor Authentication',
    '6.2.21': 'Finding the Google Authenticator app on the phone',
    '6.2.22': 'The QR code to scan with the authenticator app, blurred for privacy',
    '6.2.23': 'The 6-digit code from the authenticator app typed into Discord',
    '6.2.24': 'The Activate button next to the 6-digit code',
    '6.2.25': 'The Download Backup Codes button',
    '7.1.1': 'The Meeting Room voice channel in the channel list',
    '7.1.2': 'Voice Connected in green in the voice status panel',
    '7.1.3': 'A green ring around the picture of the person who is talking',
    '7.1.4': 'The microphone button in the user panel after muting',
    '7.1.5': 'The microphone button in the user panel after unmuting',
    '7.1.6': 'The Disconnect button (a phone icon) next to Voice Connected',
    '7.1.7': 'Joined to the Meeting Room voice channel with members listed under it',
    '7.1.8': 'The Video button (a camera icon) in the voice status panel',
    '7.1.9': 'The camera preview in the Ready to video chat window',
    '7.1.10': 'The Turn On Camera button in the preview window',
    '7.2.1': 'Joined to the Meeting Room voice channel with members listed under it',
    '7.2.2': 'Browser tabs to close before sharing your screen',
    '7.2.3': 'The Share Your Screen button in the voice status panel',
    '7.2.4': 'The Applications and Entire Screen tabs in the screen share window',
    '7.2.5': 'Clicking the window to share',
    '7.2.6': 'The Stop Streaming button in the voice status panel',
    '9.1.1': 'The microphone button with a red line through it in the user panel',
    '9.1.2': 'The headphone button with a red line through it in the user panel',
    '9.1.3': 'The red server mute icons next to a name under the voice channel',
    '9.1.4': 'The gear icon (User Settings) in the user panel',
    '9.1.5': 'Voice & Video in the list on the left of User Settings',
    '9.1.6': 'Voice under Voice & Video in the list on the left',
    '9.1.7': 'The Microphone menu in the Voice settings',
    '9.1.8': 'Choosing the microphone you are using from the Microphone menu',
    '9.1.9': 'The Microphone Volume slider',
    '9.1.10': 'The Push to Talk switch in the Voice settings',
    '9.1.11': 'The Mic Test button',
    '9.1.12': 'The Mic Test bar moving while you speak',
    '9.1.13': 'The Stop Testing button',
    '9.1.14': 'Windows Settings open after pressing Windows key + I',
    '9.1.15': 'Privacy & security in the list on the left of Windows Settings',
    '9.1.16': 'Microphone under App permissions in Privacy & security',
    '9.1.17': 'The Let desktop apps access your microphone switch and the Discord switch',
    '9.1.18': 'The headphone button with a red line through it in the user panel',
    '9.1.19': "Right-clicking a teammate's name under the voice channel",
    '9.1.20': 'The User Volume slider in the right-click menu',
    '9.1.21': 'The Mute check box in the right-click menu',
    '9.1.22': 'The gear icon (User Settings) in the user panel',
    '9.1.23': 'Voice & Video in the list on the left of User Settings',
    '9.1.24': 'The Speaker menu in the Voice settings',
    '9.1.25': 'Choosing the speakers or headphones you are using from the Speaker menu',
    '9.1.26': 'The Speaker Volume slider',
    '9.1.27': 'The speaker icon at the bottom-right of the Windows taskbar',
    '9.1.28': 'The Windows volume slider',
    '9.1.29': 'Closing another app that may be using the camera',
    '9.1.30': 'The gear icon (User Settings) in the user panel',
    '9.1.31': 'Voice & Video in the list on the left of User Settings',
    '9.1.32': 'Camera under Voice & Video in the list on the left',
    '9.1.33': 'The Camera menu in the Camera settings',
    '9.1.34': 'Choosing the camera you are using from the Camera menu',
    '9.1.35': 'The Test Video button',
    '9.1.36': 'Windows Settings open after pressing Windows key + I',
    '9.1.37': 'Privacy & security in the list on the left of Windows Settings',
    '9.1.38': 'The Camera page in Privacy & security',
    '9.1.39': 'The Camera access switch',
    '9.1.40': 'The Let desktop apps access your camera switch',
    '9.1.41': 'Right-clicking the Discord icon in the Windows notification area',
    '9.1.42': 'Quit Discord in the right-click menu',
    '9.1.43': 'Opening Discord again from the Start menu',
    '9.2.1': 'A category name in the channel list with an arrow pointing right',
    '9.2.2': 'The server name at the top of the channel list',
    '9.2.3': 'The Hide Muted Channels check box in the server menu',
    '9.2.4': 'Right-clicking the grayed-out channel',
    '9.2.5': 'Unmute Channel in the right-click menu',
    '9.2.6': 'The name in the user panel',
    '9.2.7': 'The plus button (Add a Server) in the server list',
    '9.2.8': 'The Join a Server button',
    '9.2.9': 'The invite link pasted into the Invite Link box',
    '9.2.10': 'The Join Server button',
    '9.2.11': 'Asking the group for a new invite link that never expires',
    '9.3.1': 'The pin icon at the top-right of the window',
    '9.3.2': 'The window that shows the problem',
    '9.3.3': 'The Windows Snipping Tool bar after pressing Windows key + Shift + S',
    '9.3.4': 'The #help channel in the channel list',
    '9.3.5': 'A short description of the problem typed in the message box',
    '9.3.6': 'The screenshot added to the message after pressing Ctrl + V',
    '9.3.7': 'The question and screenshot in the channel after pressing Enter',
    '9.3.8': 'A reply that says what fixed the problem',
}


def render_media(label, todo, section):
    for ext in ('webp', 'png', 'gif', 'jpg'):
        if os.path.exists(f'media/{label}.{ext}'):
            alt = html.escape(MEDIA.get(label, todo), quote=True)
            return (f'<figure class="media"><a class="media-frame" href="media/{label}.{ext}" target="_blank" rel="noopener" '
                    f'aria-label="Open {label} full size"><img src="media/{label}.{ext}" alt="{alt}" loading="lazy" decoding="async"></a>'
                    f'<figcaption>Figure {label}: {alt}</figcaption></figure>')
    if os.path.exists(f'media/{label}.mp4'):
        alt = html.escape(MEDIA.get(label, todo), quote=True)
        return (f'<figure class="media"><div class="media-frame"><video controls preload="metadata" playsinline '
                f'poster="media/{label}-poster.jpg" aria-label="{alt}"><source src="media/{label}.mp4" type="video/mp4"></video>'
                f'<a class="open-new" href="media/{label}.mp4" target="_blank" rel="noopener">Open video in a new window</a></div>'
                f'<figcaption>Figure {label}: {alt}</figcaption></figure>')
    note = f'<!-- MEDIA PLACEHOLDER {label}: {todo}. Save your file as media/{label}.png, .gif, or .mp4. -->'
    return note + f'<figure class="media placeholder"><p class="placeholder-text">Image Will Go Here</p><figcaption>Figure {label}</figcaption></figure>'


def number_media(body, num):
    count = [0]
    def rep(m):
        count[0] += 1
        return render_media(f'{num}.{count[0]}', html.unescape(m.group(1)), num.split('.')[0])
    return re.sub(r'@@MEDIA\[(.*?)\]@@', rep, body)


def steps(*items):
    """Numbered steps. Every step gets its own media spot: step text first, media centered below it."""
    out = []
    for it in items:
        text = it[0] if isinstance(it, tuple) else it
        todo = re.sub(r'<[^>]+>', '', text)
        out.append(f'<li><div class="step-text">{text}</div><div class="step-media">{media("Step: " + todo)}</div></li>')
    return '<ol class="steps steps-grid">' + ''.join(out) + '</ol>'


def explain():
    """Spot for a short paragraph that explains a figure before it is shown (to be written by Sebastian)."""
    return '<p class="placeholder-text explain">Explanatory paragraph will go here</p>'


def writing(text='Writing will go here'):
    """Spot for text Sebastian will write."""
    return f'<p class="placeholder-text writing">{text}</p>'


def todo_steps():
    """Spot for numbered steps Sebastian will write, with its image placeholder."""
    return ('<ol class="steps steps-grid"><li><div class="step-text"><span class="placeholder-text">Steps will go here</span></div>'
            f'<div class="step-media">{media("Step to be written")}</div></li></ol>')


def result(h):
    return f'<p class="result"><strong>Result:</strong> {h}</p>'


def ui(label):
    return f'<strong class="ui">{label}</strong>'


def kbd(k):
    return f'<kbd>{k}</kbd>'


# ---------------------------------------------------------------------------
# Site structure. Each entry: (number, file, title, summary, [subsections])
# Subsection: (number, file, title, summary)
# ---------------------------------------------------------------------------
SECTIONS = [
    ('1', 'about-this-tutorial.html', 'About This Tutorial', 'What you will be able to do and what you need before you begin.', [
        ('1.1', 'who-this-is-for.html', 'Who This Tutorial Is For', 'The skills, equipment, and time you need before you start.'),
        ('1.2', 'how-to-use.html', 'How to Use This Tutorial', 'How the pages, steps, notes, and new words work.'),
    ]),
    ('2', 'getting-started.html', 'Getting Started: Creating Your Account', 'Install Discord on your computer and create your account.', [
        ('2.1', 'download-app.html', 'Downloading the Desktop App', 'Install Discord on a Windows PC.'),
        ('2.2', 'sign-up.html', 'Signing Up and Verifying Your Email', 'Register, choose your names, and confirm your email address.'),
        ('2.3', 'profile-settings.html', 'Setting Up Your Profile and Comfort Settings', 'Add an avatar and pronouns, change the language, and make text larger.'),
    ]),
    ('3', 'joining-a-server.html', 'Joining Your Class or Group Server', 'Join the server your group invited you to and set your name there.', [
        ('3.1', 'what-is-a-server.html', 'What a Server Is', 'How servers, channels, and members fit together.'),
        ('3.2', 'accept-invite.html', 'Accepting an Invite Link', 'Join from a link, or paste the link into Discord.'),
        ('3.3', 'server-nickname.html', 'Setting a Server Nickname', 'Use your full name in one server only.'),
    ]),
    ('4', 'discord-layout.html', 'Understanding the Discord Layout', 'A guided tour of the Discord window from left to right.', [
        ('4.1', 'four-areas.html', 'The Four Main Areas of the Screen', 'The server list, channel list, chat area, and member list.'),
        ('4.2', 'channels.html', 'Text Channels and Voice Channels', 'Tell the two kinds of channels apart by their icons.'),
        ('4.3', 'user-panel.html', 'Your User Panel', 'The microphone, headphone, and settings buttons.'),
    ]),
    ('5', 'communicating.html', 'Communicating with Your Group', 'Send messages, use mentions, catch up, and share files.', [
        ('5.1', 'messages.html', 'Sending Messages and Direct Messages', 'Type, edit, reply, react, message privately, and use threads.'),
        ('5.2', 'mentions.html', 'Using Mentions', 'Notify one teammate, a role, or the whole server.'),
        ('5.3', 'missed-messages.html', 'Finding Messages You Missed', 'Unread indicators, the Inbox, pinned messages, and search.'),
        ('5.4', 'files.html', 'Sharing and Finding Files', 'Upload documents and find them again later.'),
    ]),
    ('6', 'notifications-privacy.html', 'Managing Notifications and Privacy', 'Control alerts and protect your account.', [
        ('6.1', 'notifications.html', 'Controlling Notifications', 'Keep important alerts and silence the rest.'),
        ('6.2', 'privacy-security.html', 'Protecting Your Privacy and Account', 'Limit who can contact you and secure your login.'),
    ]),
    ('7', 'voice-and-screen.html', 'Joining Voice Calls and Sharing Your Screen', 'Attend group meetings and present your work.', [
        ('7.1', 'voice-video.html', 'Joining a Voice Channel and Turning On Video', 'Connect, mute, disconnect, and use your camera.'),
        ('7.2', 'screen-share.html', 'Sharing Your Screen', 'Present one window or your entire screen.'),
        ('7.3', 'meeting-etiquette.html', 'Meeting Etiquette for Group Projects', 'Habits that keep group calls smooth.'),
    ]),
    ('8', 'conclusion.html', 'Next Steps', 'Review what you learned and keep going.', [
        ('8.1', 'checklist.html', 'Quick-Start Checklist', 'The core skills in one list.'),
        ('8.2', 'beyond.html', 'Beyond Your Group Project', 'Using Discord for clubs and future classes.'),
    ]),
    ('9', 'troubleshooting.html', 'Troubleshooting Common Problems', 'Fixes organized by problem.', [
        ('9.1', 'audio-video-problems.html', 'Audio and Video Problems', 'Fix microphone, speaker, and camera problems.'),
        ('9.2', 'channel-invite-problems.html', 'Channel and Invite Problems', 'Fix missing channels and expired invites.'),
        ('9.3', 'getting-help.html', 'Getting More Help', 'Ask your server for help the right way.'),
    ]),
    ('10', 'final-conclusion.html', 'Conclusion', 'Congratulations, plus official Discord help links for later.', []),
    ('11', 'glossary.html', 'Glossary', 'Every new word in this tutorial, defined in plain language.', []),
    ('12', 'credits.html', 'Credits', 'The sources and tools used to make this tutorial.', []),
]

# Flat reading order for previous / next links
ORDER = [('', 'index.html', 'Home', None)]
for num, f, title, summ, subs in SECTIONS:
    ORDER.append((num, f, title, None))
    for snum, sf, stitle, ssumm in subs:
        ORDER.append((snum, sf, stitle, (num, f, title)))


def sidebar(current):
    hcur = ' aria-current="page"' if current == 'index.html' else ''
    out = [f'<li><a class="sec" href="index.html"{hcur}>Home</a></li>']
    for num, f, title, summ, subs in SECTIONS:
        cur = ' aria-current="page"' if f == current else ''
        out.append(f'<li><a class="sec" href="{f}"{cur}><span class="n">{num}.</span> {title}</a>')
        if subs:
            out.append('<ul>')
            for snum, sf, stitle, ssumm in subs:
                scur = ' aria-current="page"' if sf == current else ''
                out.append(f'<li><a class="sub" href="{sf}"{scur}><span class="n">{snum}</span> {stitle}</a></li>')
            out.append('</ul>')
        out.append('</li>')
    return '<ul class="toc-list">' + ''.join(out) + '</ul>'


def numlabel(n):
    if not n:
        return ''
    return (n + '. ') if '.' not in n else (n + ' ')


def page(filename, body, description, draft=False):
    idx = next(i for i, o in enumerate(ORDER) if o[1] == filename)
    num, _, title, parent = ORDER[idx]
    prev = ORDER[idx - 1] if idx > 0 else None
    nxt = ORDER[idx + 1] if idx + 1 < len(ORDER) else None
    crumbs = '' if filename == 'index.html' else '<a href="index.html">Home</a>'
    if parent:
        crumbs += f' <span aria-hidden="true">/</span> <a href="{parent[1]}">Section {parent[0]}</a>'
        crumbs += f' <span aria-hidden="true">/</span> <span aria-current="page">{num}</span>'
    elif filename != 'index.html':
        crumbs += f' <span aria-hidden="true">/</span> <span aria-current="page">Section {num}</span>'
    label = f'Section {num}' if parent is None else f'Subsection {num}'
    pager = '<nav class="pager" aria-label="Previous and next pages">'
    if prev:
        pager += f'<a class="prev" href="{prev[1]}"><small>Previous</small><span>{numlabel(prev[0])}{prev[2]}</span></a>'
    else:
        pager += '<span></span>'
    if nxt:
        pager += f'<a class="next" href="{nxt[1]}"><small>Next</small><span>{numlabel(nxt[0])}{nxt[2]}</span></a>'
    pager += '</nav>'
    draft_banner = (f'<p class="draft">This {"section" if parent is None else "subsection"} is unfinished.</p>'
                    if draft else '')
    heading = f'{num}. {title}' if parent is None else f'{num} {title}'
    doc_title = 'Home' if filename == 'index.html' else (f'Section {num}. {title}' if parent is None else f'Subsection {num} {title}')
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{doc_title}</title>
<meta name="description" content="{html.escape(description, quote=True)}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Figtree:wght@400;600;700;800&display=swap" rel="stylesheet">
<link rel="icon" type="image/png" href="favicon.png">
<link rel="stylesheet" href="styles.css">
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
<div class="shell">
  <aside class="sidebar" id="sidebar" aria-label="Table of Contents">
    <a class="brand" href="index.html"><span class="brand-mark">{LOGO}</span><span>{TITLE}</span></a>
    <h2 class="toc-title">Table of Contents</h2>
    <nav aria-label="Table of Contents">{sidebar(filename)}</nav>
  </aside>
  <div class="main-col">
    <header class="topbar">
      <button class="toc-toggle" aria-expanded="false" aria-controls="sidebar">{ICON['menu']}<span>Table of Contents</span></button>
      <span class="topbar-title">{TITLE}</span>
    </header>
    <main id="main" class="content">
      {f'<nav class="crumbs" aria-label="Breadcrumb">{crumbs}</nav>' if crumbs else ''}
      {'' if filename == 'index.html' else f'<h1>{heading}</h1>'}
      {draft_banner}
{body}
{pager}
    </main>
  </div>
</div>
<div class="term-tip" id="term-tip" role="tooltip" hidden></div>
<script src="script.js"></script>
</body>
</html>
'''


def overview(num):
    """Pathway list of links + short descriptions for a section page."""
    sec = next(s for s in SECTIONS if s[0] == num)
    items = ''.join(f'<li><a href="{sf}"><span class="n">{snum}</span> {st}</a><p>{ss}</p></li>' for snum, sf, st, ss in sec[4])
    return f'<ul class="pathway">{items}</ul>'


PAGES = {}

# ===========================================================================
# SECTION 1  INTRODUCTION (homepage: What Discord Is)
# ===========================================================================
PAGES['index.html'] = ('Learn what Discord is and why your class or group uses it, then learn the Discord desktop app one short section at a time.', f'''
<h1 class="home-title">{TITLE}</h1>
<p class="lead"><a href="https://discord.com">Discord</a> is a free app that keeps a group's messages, files, and meetings in one place. This page explains how Discord is organized and why your group chose it.</p>

<h2>What Discord does</h2>
<p>Discord combines three tools that groups usually keep separate:</p>
<ul>
  <li><strong>Typed chat</strong> for questions, updates, and links</li>
  <li><strong>Voice and video calls</strong> for meetings</li>
  <li><strong>File sharing</strong> for drafts, slides, and images</li>
</ul>
<p>Each group gets its own {T('server')}. Inside the server, conversations are split into {T('channel', 'channels')}, and each channel has one topic, such as announcements or file drafts. Because topics stay separate, you can go straight to the information you need instead of scrolling through one long chat.</p>

<h2>Why classes and clubs choose Discord</h2>
<p>Many UCF project groups and student organizations use Discord for four reasons:</p>
<ul>
  <li><strong>It is free:</strong> Every feature in this tutorial works without a paid plan.</li>
  <li><strong>It is organized by topic:</strong> Announcements, files, and casual chat each have their own channel.</li>
  <li><strong>Meetings need no link:</strong> A meeting room stays open, so members join with one click instead of waiting for a new meeting link.</li>
  <li><strong>It works on every device:</strong> The desktop app, the browser version, and the phone app all show the same messages.</li>
</ul>

{note('Discord is also popular for gaming, but you do not need any gaming experience. A school server only contains the channels your group creates.')}

<h2>Start here</h2>
<p>Start with <a href="about-this-tutorial.html">Section 1: About This Tutorial</a>, or go straight to <a href="getting-started.html">Section 2: Creating Your Account</a> if you are ready to install Discord.</p>
''')

PAGES['about-this-tutorial.html'] = ('What this tutorial teaches and what you need before you begin.', f'''
<p class="lead">Your group says everything is on Discord, but you are not sure where to look. This tutorial will teach you how to use the Discord {T('desktop app')} for a class or group project, from creating your account to joining your group's meetings.</p>

<p>You can use Discord on a computer, in a web browser, or on a phone. This tutorial covers <strong>only the desktop app for Windows</strong>, so every step and every picture matches what you see on your computer screen.</p>

<h2>What you will be able to do</h2>
<ul>
  <li>Create an account and set up a profile your teammates recognize</li>
  <li>Join your group's server and find the right channels</li>
  <li>Send messages, reply, and share files</li>
  <li>Find deadlines and meeting changes you missed</li>
  <li>Join voice meetings and share your screen</li>
</ul>

<h2>Before you begin</h2>
<table class="facts">
  <tr><th scope="row">Skill level</th><td>You only need to be comfortable with email, a web browser, and messaging apps.</td></tr>
  <tr><th scope="row">You need</th><td>A Windows 10 or 11 PC, an internet connection, and an email address you can access</td></tr>
  <tr><th scope="row">Voice/Video Calls</th><td>A microphone and speakers or headphones. A webcam is optional.</td></tr>
  <tr><th scope="row">Time</th><td>About 10–30 minutes per section. Some sections are longer than others.</td></tr>
</table>

<h2>In this section</h2>
{overview('1')}
''')

PAGES['who-this-is-for.html'] = ('The audience, skills, equipment, and time this tutorial expects.', f'''
<p class="lead">This tutorial is for students who have never used Discord and need it for a class, group project, or student organization.</p>

<h2>Who will get the most from this tutorial</h2>
<p>You will get the most from this tutorial if you:</p>
<ul>
  <li>Already use apps such as email, Canvas, WhatsApp, or Zoom. You do not need to know all of them.</li>
  <li>Have a group that asked you to join their Discord server</li>
  <li>Want to keep up with messages without spending hours learning a new app</li>
</ul>

<h2>What you need before you start</h2>
<ul>
  <li>A Windows 10 or 11 PC</li>
  <li>An internet connection</li>
  <li>An email address you can check right away, such as your Knights email</li>
  <li>A microphone and speakers or headphones for voice and video calls</li>
</ul>

{caution('Library and work computers often block new programs from being installed. Use your own computer for this tutorial so you can install the desktop app.')}

<h2>What you do not need to know</h2>
<p>You do not need to know any Discord words before you begin. Every new word appears in <span class="term-sample">blue</span> text the first time it is used on a page. Point to the blue word with your mouse to read its definition. All new words are also collected in the <a href="glossary.html">Glossary</a>.</p>
''')

PAGES['how-to-use.html'] = ('How the pages, numbered steps, notes, cautions, and new words in this tutorial work.', f'''
<p class="lead">This tutorial is divided into short sections. Each section has its own page, and each topic inside a section has its own page, so you can stop and return at any time.</p>

<h2>Navigation</h2>
<p>Each section builds on the one before it. Use the <strong>Table of Contents</strong> on the left to jump to any page, or use the <strong>Previous</strong> and <strong>Next</strong> buttons at the bottom of each page to go back or keep reading in order.</p>

<h2>Keep the tutorial and Discord side by side</h2>
<p>Open this tutorial in your web browser on one half of your screen and the Discord app on the other half. You can then read a step and complete it without switching windows.</p>
{note('Complete <a href="download-app.html">Subsection 2.1</a> first if you have not installed Discord yet.')}
{steps(
    'Open this tutorial in your web browser.',
    f'Press {kbd("Windows key")} + {kbd("Left Arrow")} to move the browser to the left half of the screen.',
    'Open the Discord app.',
    f'Press {kbd("Windows key")} + {kbd("Right Arrow")} to move Discord to the right half of the screen.',
)}

<h2>How each page is written</h2>
<ul>
  <li><strong>Numbered steps</strong> tell you one action at a time. Complete them in order.</li>
  <li><strong>Bold words</strong> such as {ui('Continue')} match the buttons and menu names on your screen.</li>
  <li><strong>Pictures</strong> appear below each step they show. Click a picture to open it in a new tab for easier viewing.</li>
  <li><strong>Blue words</strong>, such as {T('server')}, are new words. Point to them to see the definition.</li>
</ul>

<h2>Notes, cautions, and results</h2>
<p>Three kinds of boxes set off extra information:</p>
{note('A Note gives extra information that helps you complete a task.')}
{caution('A Caution warns you about something that could cause a problem with your account or your work.')}
{result('A Result appears after a set of steps and tells you what you should see when you finish them correctly. If your screen does not match, go back and check each step.')}
''')

# ===========================================================================
# SECTION 2  GETTING STARTED
# ===========================================================================
PAGES['getting-started.html'] = ('Install the Discord desktop app and create your account.', f'''
<p class="lead">In this section, you will install the {T('desktop app')}, create your account, and set up a profile your teammates recognize.</p>
<p><strong>You need:</strong> your computer and an email address you can check.</p>
{overview('2')}
''')

PAGES['download-app.html'] = ('Download and install the Discord desktop app on Windows.', f'''
<p class="lead">The {T('desktop app')} is the most complete version of Discord and the version this tutorial uses. Installing it takes about five minutes.</p>

<h2>Install Discord on Windows</h2>
{steps(
    'Open your web browser and go to <strong>discord.com/download</strong>.',
    (f'Click {ui("Download for Windows")}.', media('Your screenshot of the download page with the Download for Windows button circled', True)),
    f'Open the file <strong>DiscordSetup.exe</strong> from your Downloads folder.',
    'Wait while Discord installs. The app opens on its own when it finishes.',
)}
{result('The Discord login screen appears, and a Discord shortcut is added to your Start menu.')}

{caution('Download Discord only from discord.com. Copies offered on other websites can contain harmful software.')}
''')

PAGES['sign-up.html'] = ('Register for a Discord account, choose your names, and verify your email.', f'''
<p class="lead">Creating your account takes about five minutes. You will choose two names, so read the short explanation below before you start.</p>

<h2>Choosing a username and display name</h2>
<p>Discord asks you for two different names:</p>
<ul>
  <li>Your {T('username')} is unique, like an email address. It can use only lowercase letters, numbers, periods, and underscores.</li>
  <li>Your {T('display name')} is the name teammates see next to your messages. It can include spaces and capital letters.</li>
</ul>
<p>For school, use a display name your classmates and instructors recognize, such as your first and last name. You can still change it later.</p>

<h2>Sign up</h2>
{steps(
    'Open the Discord app.',
    (f'On the login screen, click {ui("Register")} under the {ui("Log In")} button.', media('Your screenshot of the login screen with Register circled', True)),
    'Type your email address.',
    'Type your display name.',
    'Type a username. If the name is taken, Discord asks you to choose another one.',
    'Type a password that you do not use for any other account.',
    'Select your month, day, and year of birth.',
    f'Click {ui("Continue")}.',
    f'Complete the {T("CAPTCHA")} puzzle, such as checking the box next to <strong>I am human</strong>.',
)}
{result('Discord opens to your home screen, and a verification email is sent to your inbox.')}
<p>Congratulations! Your Discord is installed and logged in. Yours should appear as shown below.</p>
{media('Home screen after signing up')}

<h2>Verify your email address</h2>
<p>Discord will not let you join some servers until you verify your email address.</p>
{steps(
    'Open your email inbox.',
    'Open the email from Discord with the subject <strong>Verify Email Address for Discord</strong>.',
    (f'Click {ui("Verify Email")}.', media('Your screenshot of the verification email with the Verify Email button circled', True)),
)}
{result('A web page opens that says your email is verified. You can close that browser tab and return to the app.')}

{note('If the email does not arrive within five minutes, check your spam or junk folder. You can also click <strong>Resend</strong> on the green bar at the top of the Discord app.')}
''')

PAGES['profile-settings.html'] = ('Add an avatar and pronouns, switch Discord to Spanish or another language, and make text larger.', f'''
<p class="lead">An avatar and pronouns help your group recognize you, and comfort settings make Discord easier to read. All three tasks on this page start in {T('User Settings')}.</p>

<h2>Open User Settings</h2>
{steps(
    'Find your name at the bottom-left corner of the Discord window.',
    (f'Click the gear icon to the right of your name.', media('Your screenshot of the bottom-left corner with the gear icon circled', True)),
)}
{result('The User Settings menu opens, with a list of options on the left. Press <kbd>Esc</kbd> at any time to close it.')}

<h2>Adding an Avatar and Pronouns</h2>
<p>Your {T('avatar')} appears next to every message you send. A clear photo of your face or a simple image helps teammates match your messages to you. Adding your pronouns helps teammates know how to refer to you.</p>
{steps(
    f'In User Settings, click {ui("Edit Profiles")}.',
    f'Click your {ui("Avatar")}, and then click the {ui("Change Avatar")} button.',
    f'Click {ui("Upload Image")}.',
    'Choose a picture from your computer.',
    'Drag the picture or use the buttons below to adjust the crop.',
    f'Click {ui("Apply")}.',
    f'Click {ui("Save")} at the bottom of the window.',
    f'Click the area that says {ui("Add pronouns")}, next to your username.',
    'Type your preferred pronouns, such as <strong>He/Him</strong>.',
    f'Click {ui("Save")}.',
)}
{result('Your new picture appears in the bottom-left corner next to your name, and your pronouns appear on your profile card.')}

<h2>Change the display language</h2>
<p>You can switch every menu and button in Discord to another language, such as Spanish. Messages from your group stay in the language they were written in.</p>
{steps(
    f'In User Settings, scroll down and click {ui("Language & Time")}.',
    f'Click the language you want, such as {ui("Español, LATAM")}.',
)}
{result('Discord changes language right away. No restart is needed.')}
{note('This tutorial uses the English names of buttons. If you change the language, switch it back to English while you work through the steps, or keep this tutorial open beside Discord to match the button positions.')}

<h2>Make text larger</h2>
{steps(
    f'In User Settings, click {ui("Accessibility")}.',
    f'Under {ui("Text Readability")}, find {ui("Text size in chat")}.',
    'Drag the slider to the right until messages are comfortable to read.',
)}
{result('Messages in every channel use the larger size.')}
{note(f'To make everything in Discord larger, including menus, press {kbd("Ctrl")} + {kbd("+")}. Press {kbd("Ctrl")} + {kbd("0")} to return to normal size.')}
''')

# ===========================================================================
# SECTION 3  JOINING A SERVER
# ===========================================================================
PAGES['joining-a-server.html'] = ('Join your class or group server from an invite link and set your name there.', f'''
<p class="lead">Joining your group's {T('server')} is usually the first thing a group asks a new member to do. This section explains what a server is, shows you how to join one, and shows you how to set your name for that server.</p>
<p><strong>You need:</strong> the invite link your group sent you.</p>
{overview('3')}
''')

PAGES['what-is-a-server.html'] = ('What a Discord server is and how one account can belong to many servers.', f'''
<p class="lead">A {T('server')} is a private space for one group, class, or club. Only people who are invited can join it.</p>

<h2>What is inside a server</h2>
<p>Every server contains the same basic parts:</p>
<ul>
  <li><strong>Members:</strong> the people who joined the server</li>
  <li>{T('channel', '<strong>Channels</strong>')}<strong>:</strong> separate areas for each topic, such as #announcements or #files-and-drafts</li>
  <li><strong>Owner and moderators:</strong> the people who set up the channels and manage the server, such as a group leader or club officer</li>
</ul>
{media('Your screenshot of a sample group project server with its channels and members visible')}

<h2>One account, many servers</h2>
<p>You only need one Discord account, even if you join servers for several classes and clubs. Each server you join appears as a round icon in the column on the far left of the Discord window. Click an icon to switch to that server.</p>
{media('Your screenshot of the server icons on the far left with several school servers', True)}

{note('Leaving a server does not delete your account. You can rejoin later if someone sends you a new invite link.')}
''')

PAGES['accept-invite.html'] = ('Join a Discord server from an invite link on your computer.', f'''
<p class="lead">Groups invite new members by sending an {T('invite link')}, usually by email, text message, or a Canvas message. The link looks like <strong>discord.gg/</strong> followed by a short code.</p>

<h2>Join by clicking the link</h2>
{steps(
    'Make sure you are logged in to the Discord desktop app.',
    f'Click the {ui("Join")} button on the invite link your group sent.',
)}
{result('Discord opens to the new server, and its icon appears in the column on the far left.')}

<h2>Join by pasting the link</h2>
<p>If clicking the link does not open the server, paste the link into Discord yourself.</p>
{steps(
    'Copy the invite link from the email or message.',
    (f'In Discord, click the plus button ({ui("Add a Server")}) near the bottom of the round server icons on the far left.', media('Your screenshot of the plus button circled in the server list', True)),
    f'At the bottom of the window that opens, click {ui("Join a Server")}.',
    f'Paste the link into the {ui("Invite Link")} box.',
    f'Click {ui("Join Server")}.',
)}
{result('The new server opens, and its icon appears in the server column on the far left. <a href="four-areas.html">Subsection 4.1</a> explains this column, called the server list.')}

{caution('If Discord says the invite is invalid or expired, ask your group for a new link. Invite links can be set to stop working after a certain time or number of uses.')}
''')

PAGES['server-nickname.html'] = ('Set a server nickname so you use your full name in one server only.', f'''
<p class="lead">A {T('server nickname')} changes your name in one server without changing it anywhere else. Use your full name in class servers so teammates and instructors know who wrote each message.</p>

<h2>Set your server nickname</h2>
{steps(
    'Click your profile in the member list.',
    f'Click {ui("Edit Profile")}, and then click {ui("Edit Per-server Profile")}.',
    'Type your nickname in the name box under your avatar.',
    f'Click {ui("Save")}.',
)}
{result('Your new nickname appears next to your messages in this server. Your name in all other servers stays the same.')}

{note('Some servers do not allow members to change their own nickname. If you do not see the option, ask a server moderator to set it for you.')}
''')

# ===========================================================================
# SECTION 4  LAYOUT
# ===========================================================================
PAGES['discord-layout.html'] = ('A guided tour of the Discord desktop window from left to right.', f'''
<p class="lead">A crowded screen is the most common reason beginners feel lost in Discord. This section walks through the window from left to right so you always know where to look.</p>
<p><strong>You need:</strong> Discord open to your group's server.</p>
{overview('4')}
''')

PAGES['four-areas.html'] = ('The server list, channel list, chat area, and member list in the Discord desktop app.', f'''
<p class="lead">The Discord window is divided into four main areas. Read them from left to right.</p>

<h2>1. Server list</h2>
<p>The {T('server list')} is the narrow column of round icons on the far left. Each icon is a server you belong to. The Discord logo at the top opens your private messages, which <a href="messages.html">Subsection 5.1</a> explains.</p>
{media('Server list')}

<h2>2. Channel list</h2>
<p>The {T('channel list')} shows every channel in the server you selected. The server name appears at the top. Channels are grouped under headings called {T('category', 'categories')}.</p>
{media('Channel list')}

<h2>3. Chat area</h2>
<p>The {T('chat area')} in the center shows the messages in the channel you selected. The newest messages are at the bottom, and the box for typing your own message is below them.</p>
{media('Chat area')}

<h2>4. Member list</h2>
<p>The {T('member list')} on the right shows who belongs to the server. Members who are online appear at the top.</p>
{media('Member list')}
{note('If you do not see the member list, click the icon of two people at the top-right of the window to show or hide it.')}
{media('Member list icon')}
''')

PAGES['channels.html'] = ('How to tell text channels and voice channels apart in Discord.', f'''
<p class="lead">Every server has two main kinds of channels. You can tell them apart by the icon in front of each channel name.</p>

<h2>Text channels</h2>
<p>A {T('text channel')} has a pound sign (<strong>#</strong>) in front of its name, such as <strong>#announcements</strong>. Text channels are for typed messages, links, and files. Click a text channel to read it.</p>
{media('Text channels with the # icon')}

<h2>Voice channels</h2>
<p>A {T('voice channel')} has a speaker icon in front of its name, such as <strong>Meeting Room</strong>. Voice channels are for live talking, video, and screen sharing.</p>
{media('Voice channels with the speaker icon')}
{caution('Clicking a voice channel connects you to it immediately, and <strong>the other people in it may hear your microphone</strong>. Click a voice channel only when you are ready to talk.')}

<h2>Bold and gray channel names</h2>
<p>A channel name in <strong>bold white</strong> has messages you have not read. A gray channel name means you are caught up. <a href="missed-messages.html">Subsection 5.3</a> explains more ways to catch up.</p>
''')

PAGES['user-panel.html'] = ('The microphone, headphone, and settings buttons in the Discord user panel.', f'''
<p class="lead">The {T('user panel')} sits at the bottom of the channel list. It shows your picture and name and three buttons that control your sound and settings.</p>
{media('Close-up screenshot of the user panel with the three buttons labeled')}

<h2>The three buttons</h2>
<table class="facts">
  <tr><th scope="col">Button</th><th scope="col">What it does</th></tr>
  <tr><td><strong>Microphone</strong></td><td>Click it to {T('mute')} or unmute your microphone. A red line through the icon means you are muted.</td></tr>
  <tr><td><strong>Headphones</strong></td><td>Click it to {T('deafen')} or undeafen yourself. A red line through the icon means you hear no sound.</td></tr>
  <tr><td><strong>Gear</strong></td><td>Opens {T('User Settings')}, where you change your profile, language, and text size.</td></tr>
</table>

<h2>Muting compared with deafening</h2>
<p>Muting turns off only your microphone, so you can still hear your group. Deafening turns off all sound in Discord and also mutes your microphone. Before a meeting, check that neither button has a red line through it.</p>
{media('GIF of clicking mute and deafen and the icons changing', True)}
{note(f'Click your picture or name in the user panel to see your profile card and change your status, such as <strong>Online</strong> or <strong>Do Not Disturb</strong>.')}
''')

# ===========================================================================
# SECTION 5  COMMUNICATING
# ===========================================================================
PAGES['communicating.html'] = ('Send messages, use mentions, catch up on missed updates, and share files in Discord.', f'''
<p class="lead">This section teaches you how to talk with your group and how to make sure you never miss a meeting change or deadline.</p>
<p><strong>You need:</strong> Discord open to a text channel in your group's server.</p>
{overview('5')}
''')

PAGES['messages.html'] = ('Type, edit, reply to, and react to messages, and use direct messages and threads.', f'''
<p class="lead">Most group work in Discord happens in typed messages. This page shows you how to send, edit, and answer messages and how to talk privately.</p>

<h2>Send a message</h2>
{steps(
    'Click a text channel in the channel list.',
    'Click the message box at the bottom of the chat area. It says <strong>Message #</strong> followed by the channel name.',
    'Type your message.',
    f'Press {kbd("Enter")} to send it.',
)}
{result('Your message appears at the bottom of the chat area for everyone in the channel.')}
{note(f'To start a new line without sending, press {kbd("Shift")} + {kbd("Enter")}.')}

<h2>Edit a message you sent</h2>
{steps(
    'Hold your pointer over your message.',
    'Click the pencil icon that appears on the right.',
    'Change the text.',
    f'Press {kbd("Enter")}.',
)}
{result('The message updates and shows <strong>(edited)</strong> next to it.')}

<h2>Reply to a message</h2>
<p>A {T('reply')} shows everyone which message you are answering, which keeps busy channels clear.</p>
{steps(
    'Hold your pointer over the message you want to answer.',
    (f'Click the {ui("Reply")} arrow on the right.', media('Your screenshot of the hover menu with the Reply arrow circled', True)),
    'Type your answer.',
    f'Press {kbd("Enter")}.',
)}

<h2>React to a message</h2>
<p>A {T('reaction')} is a quick way to say "I saw this" without adding another message.</p>
{steps(
    'Hold your pointer over the message.',
    f'Click the smiley face icon ({ui("Add Reaction")}).',
    'Click an emoji, such as a thumbs up.',
)}
{result('The emoji appears under the message with a count of how many people chose it.')}
{media('Reaction result')}

<h2>Send a direct message</h2>
<p>A {T('direct message')} (DM) is a private conversation outside the server channels.</p>
{steps(
    'Click a teammate\'s name in the member list.',
    f'Type your message in the {ui("Message @")} box on their profile card.',
    f'Press {kbd("Enter")}.',
)}
{result('A private conversation opens. To find it later, click the Discord logo at the top of the server list.')}

<h2>Start a thread</h2>
<p>A {T('thread')} keeps a long side discussion about one message out of the main channel.</p>
{steps(
    'Hold your pointer over the message you want to discuss.',
    f'Click the three dots ({ui("More")}).',
    f'Click {ui("Create Thread")}.',
    'Type a short name for the thread.',
    'Type your first message.',
    f'Press {kbd("Enter")}.',
)}
''')

PAGES['mentions.html'] = ('Mention a teammate, a role, or the whole server in Discord.', f'''
<p class="lead">A {T('mention')}, also called a ping, sends a notification to the people you name. Use mentions when someone needs to see a message soon.</p>

<h2>Mention a teammate</h2>
{steps(
    'In the message box, type <strong>@</strong>.',
    'Type the first few letters of your teammate\'s name.',
    (f'Click their name in the list that appears.', media('Your screenshot of the @ suggestion list above the message box', True)),
    'Finish typing your message.',
    f'Press {kbd("Enter")}.',
)}
{result('Your teammate receives a notification, and the message is highlighted for them.')}
{note('When someone mentions you, the message has a yellow highlight and a yellow bar on its left edge, so you can spot it while scrolling.')}

<h2>Mention a group of people</h2>
<p>Three special mentions reach more than one person:</p>
<table class="facts">
  <tr><th scope="col">Mention</th><th scope="col">Who is notified</th><th scope="col">When to use it</th></tr>
  <tr><td><strong>@everyone</strong></td><td>Every member of the server</td><td>Rarely, for changes that affect the whole group, such as a new meeting time</td></tr>
  <tr><td><strong>@here</strong></td><td>Only members who are online right now</td><td>For something happening now, such as "the call is starting"</td></tr>
  <tr><td><strong>@</strong> and a {T('role')} name</td><td>Only members with that role, such as @Presenters</td><td>For tasks that involve part of the group</td></tr>
</table>

{caution(f'Overusing @everyone and @here annoys teammates and can lead them to turn off notifications. Many servers allow only a {T("moderator")} to use them.')}
''')

PAGES['missed-messages.html'] = ('Catch up on missed Discord messages with unread indicators, the Inbox, pinned messages, and search.', f'''
<p class="lead">After a day away from Discord, use these four tools to find deadlines and meeting changes quickly.</p>

<h2>Unread indicators and mention badges</h2>
<ul>
  <li>An {T('unread indicator')} is a white dot to the left of a server icon or a bold channel name. It means there are new messages.</li>
  <li>A {T('mention badge')} is a red circle with a number. It means someone mentioned you, and the number shows how many times.</li>
</ul>
<p>Check channels with a red badge first, because those messages are meant for you.</p>

<h2>Use the Inbox</h2>
<p>The {T('Inbox')} collects recent mentions from every server in one list.</p>
{steps(
    'Click the tray icon at the top-right of the Discord window.',
    f'Click the {ui("Mentions")} tab.',
    f'Click {ui("Jump")} next to a message to open it in its channel.',
)}
{result('The message opens in its channel.')}

<h2>Check pinned messages</h2>
<p>Groups often save deadlines and meeting links as a {T('pinned message', 'pinned message')}.</p>
{steps(
    'Open the channel you want to check.',
    'Click the pin icon at the top-right of the window.',
    f'Click {ui("Jump")} next to a pinned message to see it in the conversation.',
)}
{result('The message opens in its channel.')}

<h2>Search for a message</h2>
{steps(
    'Click the <strong>Search</strong> box at the top-right of the window.',
    'Type a word from the message, such as <strong>deadline</strong>.',
    f'Press {kbd("Enter")}.',
    'Click a result to jump to that message.',
)}
{result('The message opens in its channel.')}
{note('To search for messages from one person, type <strong>from:</strong> in the Search box, and then pick the person from the list.')}
''')

PAGES['files.html'] = ('Upload files to Discord and find shared files later.', f'''
<p class="lead">Group projects depend on drafts, slides, and images. This page shows you how to share an {T('attachment')} and how to find files your group already shared.</p>

<h2>Upload a file</h2>
{steps(
    'Open the channel where your group shares files, such as #files-and-drafts.',
    'Click the plus button on the left side of the message box.',
    f'Click {ui("Upload a File")}.',
    'Choose the file on your computer.',
    'Click <strong>Open</strong>.',
    'Type a short message that explains the file, such as "Draft of my section."',
    f'Press {kbd("Enter")}.',
)}
{result('The file appears in the channel, and teammates can open or download it.')}
{note('You can also drag a file from your desktop or a folder and drop it into the chat area.')}
{caution('Free Discord accounts have a file size limit, currently 20 MB per file, and Discord sometimes changes it. For larger files, upload them to OneDrive or Google Drive and paste the link instead.')}

<h2>Find files later</h2>
{steps(
    'Click the <strong>Search</strong> box at the top-right of the window.',
    'Type <strong>has:</strong> in the Search box.',
    'Click <strong>file</strong> in the list.',
    f'Press {kbd("Enter")}.',
)}
{result('Discord lists every message in the server that includes a file, with the newest first.')}
{note('Ask your group to pin the final version of each file in the files channel so everyone uses the same copy.')}
''')

# ===========================================================================
# SECTIONS 6 to 9  (in progress) and GLOSSARY
# ===========================================================================
DRAFTS = {
    'notifications-privacy.html': 'This section teaches you how to control how often Discord interrupts you and who can contact you.',
    'notifications.html': 'Discord can alert you for every message, which quickly becomes distracting. This page shows you how to keep the alerts that matter and silence the rest.',
    'privacy-security.html': 'You decide who can contact you on Discord and how well your account is protected. This page shows you how to limit messages from strangers and secure your login.',
    'voice-and-screen.html': 'This section teaches you how to attend group meetings in a voice channel and present your work by sharing your screen.',
    'voice-video.html': 'Group meetings on Discord happen in voice channels. This page shows you how to join a call, control your microphone, and turn on your camera.',
    'screen-share.html': 'Sharing your screen lets your group see your slides, documents, or code during a call. This page shows you how to start and stop a share.',
    'meeting-etiquette.html': 'A few simple habits keep group calls short and focused. Use them before and during every meeting.',
    'conclusion.html': 'This section reviews the skills you learned and shows you how to keep using Discord after your project ends.',
    'checklist.html': 'Use this checklist to confirm you can do each core skill from this tutorial before your next group meeting.',
    'beyond.html': 'The skills in this tutorial work in every Discord server, not just your group project. This page explains how to use them in clubs and future classes.',
    'troubleshooting.html': 'This section is a quick-reference guide organized by problem, so you can find a fix without rereading the tutorial.',
    'audio-video-problems.html': 'Most audio and video problems come from a muted button, the wrong device, or a Windows permission. Find your problem below and follow its fixes in order.',
    'channel-invite-problems.html': 'Missing channels and broken invite links usually have a simple cause. Find your problem below and follow its fixes in order.',
    'getting-help.html': 'When this tutorial does not solve your problem, the members and moderators of your server can help. This page shows you how to ask a clear question.',
}
# "You need" line shown under the lead of each section page
YOU_NEED = {
    'notifications-privacy.html': "Discord open to your group's server. For two-factor authentication, you also need your phone.",
    'voice-and-screen.html': "Discord open to your group's server, and a microphone and speakers or headphones. A webcam is optional.",
    'conclusion.html': "Discord open to your group's server, so you can try each skill on the checklist.",
    'troubleshooting.html': "Discord open on your computer. For audio and video fixes, connect your microphone, speakers or headphones, and webcam.",
}
# Headings follow the Project 2.2 outline. Placeholders mark where Sebastian's own
# steps, writing, and images will go.
SCAFFOLD = {
    'notifications.html': [('Server Notification Settings', 'steps'), ('Muting and Do Not Disturb', 'steps')],
    'privacy-security.html': [('Message and Friend Request Settings', 'steps'), ('Account Security', 'steps')],
    'voice-video.html': [('Connecting, Muting, and Disconnecting', 'steps'), ('Turning On Your Camera', 'steps')],
    'screen-share.html': [('Choosing a Window or Entire Screen', 'steps'), ('Stopping a Share', 'steps')],
    'meeting-etiquette.html': [('Before the Call', 'text'), ('During the Call', 'text')],
    'checklist.html': [('Core Skills Checklist', 'text')],
    'beyond.html': [('Student Organizations and Future Classes', 'text')],
    'audio-video-problems.html': [('Others Cannot Hear Me', 'steps'), ('I Cannot Hear Others', 'steps'), ('My Camera Will Not Turn On', 'steps')],
    'channel-invite-problems.html': [('I Cannot See a Channel', 'steps'), ('An Invite Link Does Not Work', 'steps')],
    'getting-help.html': [('Asking Your Server for Help', 'steps')],
}
# Written steps for the subsections in Sections 6, 7, and 9. Any heading not listed
# here still shows the "Steps will go here" placeholder.
VS = T('voice status panel')
GEAR = f'Click the gear icon ({ui("User Settings")}) in the user panel.'
STEPS = {
    # ---------------- 6.1 Controlling Notifications ----------------
    ('notifications.html', 'Server Notification Settings'): f'''
<p>Each server has its own notification settings. For most class servers, {ui('Only @mentions')} is the best choice: Discord alerts you when someone needs you and stays quiet the rest of the time.</p>
{steps(
    "Right-click your group's server icon in the server list.",
    f'Click {ui("Notification Settings")}.',
    f'Under {ui("Server Notification Settings")}, click {ui("Only @mentions")}.',
    f'If @everyone and @here messages interrupt you too often, turn on the {ui("Suppress @everyone and @here")} switch.',
)}
{result('Discord notifies you only when someone mentions you by name, mentions one of your roles, or sends you a direct message. Other messages still appear as bold channel names, so you can catch up when you are ready.')}
{note('These settings apply to one server at a time. Repeat the steps for each server you belong to.')}
{caution(f'Do not choose {ui("Nothing")} for a class or project server. With Nothing selected, you will not be alerted when a teammate mentions you about a deadline or a meeting change.')}
''',
    ('notifications.html', 'Muting and Do Not Disturb'): f'''
<p>Muting silences one server or channel for a set time. {T('Do Not Disturb')} silences all of Discord, which is useful during class, work, or an exam.</p>
<h3>Mute a server or a channel</h3>
{steps(
    'Right-click the server icon in the server list.',
    f'Point to {ui("Mute Server")}.',
    f'Click how long to mute it, such as {ui("For 1 Hour")} or {ui("Until I turn it back on")}.',
)}
{result('The muted server turns gray and stops showing unread indicators. If someone mentions you there, you still see a red mention badge.')}
{note(f'To mute only one channel, right-click the channel name in the channel list instead, and then point to {ui("Mute Channel")}. To end a mute early, right-click the server or channel again and click {ui("Unmute Server")} or {ui("Unmute Channel")}.')}
<h3>Turn on Do Not Disturb</h3>
{steps(
    'Click your picture in the user panel at the bottom-left of the window.',
    'Point to your current status, such as <strong>Online</strong>.',
    f'Point to {ui("Do Not Disturb")}.',
    f'Click how long to stay in Do Not Disturb, such as {ui("For 1 Hour")}.',
)}
{result('A red circle appears on your picture, and Discord stops showing desktop notifications and playing notification sounds. Messages still arrive, so you can read them later.')}
{note(f'To turn Do Not Disturb off early, click your picture, point to your status, and click {ui("Online")}.')}
''',
    # ---------------- 6.2 Protecting Your Privacy and Account ----------------
    ('privacy-security.html', 'Message and Friend Request Settings'): f'''
<p>By default, anyone who shares a server with you can send you a direct message. These steps let you decide who can contact you.</p>
<h3>Limit who can send you direct messages</h3>
{steps(
    GEAR,
    f'Click {ui("Messaging Permissions")} in the list on the left.',
    f'Under {ui("Direct Message (DM) Permissions")}, click {ui("All Servers")} at the top.',
    f'Turn off the {ui("Direct Messages")} switch.',
    f'When Discord asks whether to apply the change to the servers you are already in, click {ui("Yes")}.',
)}
{result('Server members who are not your friends can no longer send you direct messages.')}
{note(f'If your project group plans by direct message, you can allow messages from one server only. In step 3, choose your class server instead of {ui("All Servers")}, and then turn the {ui("Direct Messages")} switch back on.')}
<h3>Limit who can send you friend requests</h3>
{steps(
    f'In {ui("Messaging Permissions")}, scroll to {ui("Friend Request Permissions")}.',
    f'Turn off {ui("Everyone")}.',
    f'If you do not want requests from people you only share a server with, turn off {ui("Server Members")}.',
)}
{result('Strangers can no longer send you friend requests. Changes save automatically.')}
{note(f'Leave {ui("Friends of Friends")} on so classmates who share a friend with you can still add you.')}
<h3>Block someone</h3>
<p>If someone sends you unwanted messages, you can {T('block')} them, report the message to Discord, or both.</p>
{steps(
    "Right-click the person's name in the member list or in the chat area.",
    f'Click {ui("Block")}.',
    f'Click {ui("Block")} again to confirm.',
)}
{result('You no longer receive direct messages from that person, and their messages in shared servers are hidden behind a notice.')}
<h3>Report a message</h3>
{steps(
    'Right-click the message you want to report.',
    f'Click {ui("Report Message")}.',
    'Click the reason that best describes the problem.',
    'On each screen that follows, click the option that fits best until Discord confirms the report was sent.',
)}
{result("Discord's safety team receives the report. The person is not told who reported them.")}
''',
    ('privacy-security.html', 'Account Security'): f'''
<p>{T('two-factor authentication', 'Two-factor authentication')} (2FA) asks for a code from your phone every time you log in on a new device, so a stolen password alone cannot open your account.</p>
<h3>Turn on two-factor authentication</h3>
{steps(
    'On your phone, install a free authenticator app, such as Google Authenticator or Authy.',
    GEAR,
    f'Click {ui("Account")} in the list on the left.',
    f'Click {ui("Password &amp; Security")}.',
    f'Under {ui("Multi-Factor Authentication")}, click {ui("Enable Authenticator App")}.',
    'Open the authenticator app on your phone.',
    'Use the app to scan the QR code that Discord shows.',
    'Type the 6-digit code from the app into Discord.',
    f'Click {ui("Activate")} and enter your Discord password if prompted.',
    f'Save your {T("backup codes")} by downloading them or writing them down, and keep them somewhere safe.',
)}
{result('Your account now asks for a 6-digit code from your phone whenever you log in on a new device.')}
{caution('If you lose your phone and your backup codes, you can be locked out of your account permanently. Keep your backup codes somewhere other than your phone.')}
<h3>Recognize common scams</h3>
<ul>
  <li><strong>"Free Nitro" or gift links:</strong> Links that promise free Discord Nitro or prizes usually lead to fake login pages. Do not click them.</li>
  <li><strong>"I accidentally reported you" messages:</strong> A stranger claims your account will be banned unless you contact a "Discord staff member." Discord staff never contact you this way.</li>
  <li><strong>QR code requests:</strong> Never scan a QR code someone sends you. Scanning it can log that person into your account.</li>
  <li><strong>Requests for your password or codes:</strong> No one from Discord, your school, or your group will ever ask for your password, 2FA codes, or backup codes.</li>
</ul>
{caution("If a teammate's account suddenly sends you a strange link, their account may have been taken over. Do not click the link, and tell them another way, such as by text or email.")}
''',
    # ---------------- 7.1 Joining a Voice Channel and Turning On Video ----------------
    ('voice-video.html', 'Connecting, Muting, and Disconnecting'): f'''
{steps(
    'Click a voice channel, such as <strong>Meeting Room</strong>, in the channel list.',
    f'Check that {ui("Voice Connected")} appears in green in the {VS} above your user panel.',
    'Speak to your group. A green ring appears around your picture while you are talking.',
    'When you are not speaking, click the microphone button in the user panel to mute yourself.',
    'When you want to speak again, click the microphone button to unmute yourself.',
    f'When the meeting ends, click the {ui("Disconnect")} button (a phone icon) to the right of {ui("Voice Connected")}.',
)}
{result('While you are connected, your name appears under the voice channel for everyone in the server. After you disconnect, your name disappears from the channel and no one can hear you.')}
{note('Discord keeps you connected while you move between text channels. You stay in the call until you click Disconnect.')}
''',
    ('voice-video.html', 'Turning On Your Camera'): f'''
{steps(
    'Join a voice channel by following the steps above.',
    f'Click the {ui("Video")} button (a camera icon) in the {VS}.',
    'If a camera preview window opens, check that your picture and background look the way you want.',
    f'Click {ui("Turn On Camera")} in the preview window.',
)}
{result('Your video appears in the call view for everyone in the voice channel. When the camera is off, teammates see your profile picture instead.')}
{note(f'To turn your camera off, click the {ui("Video")} button again. To check your camera before a meeting, open {ui("User Settings")}, click {ui("Camera")} under {ui("Voice &amp; Video")}, and click {ui("Test Video")}.')}
''',
    # ---------------- 7.2 Sharing Your Screen ----------------
    ('screen-share.html', 'Choosing a Window or Entire Screen'): f'''
<p>You can {T('screen share', 'share your screen')} in any voice channel where your server allows it. Sharing one window is usually safer, because teammates see only that window and not your notifications or other open apps.</p>
{steps(
    'Join a voice channel. <a href="voice-video.html">Subsection 7.1</a> shows how.',
    'Close any windows or browser tabs that show private information, such as your email or bank account.',
    f'Click the {ui("Share Your Screen")} button (a monitor with an arrow) in the {VS}.',
    f'Click the {ui("Applications")} tab to share one window, or the {ui("Entire Screen")} tab to share everything on your monitor.',
    'Click the window or screen you want to share.',
)}
{result(f'A small preview of your share appears, and a red {ui("LIVE")} label appears next to your name in the voice channel. Teammates click your name to watch.')}
{note(f'Leave the quality settings as they are unless your group asks you to change them. To share a video with sound, such as a clip in your slides, turn on the sound option before you start sharing.')}
''',
    ('screen-share.html', 'Stopping a Share'): f'''
{steps(
    f'Click the {ui("Stop Streaming")} button (a monitor with an X) in the {VS}.',
)}
{result(f'Your share ends, and the {ui("LIVE")} label disappears from your name. You stay connected to the voice channel, so you can keep talking.')}
{note(f'Clicking {ui("Disconnect")} also stops your share, but it removes you from the call.')}
''',
    # ---------------- 9.1 Audio and Video Problems ----------------
    ('audio-video-problems.html', 'Others Cannot Hear Me'): f'''
<p>Work through these steps in order. Stop as soon as your group can hear you.</p>
{steps(
    'If the microphone button in the user panel has a red line through it, click it to unmute yourself.',
    'If the headphone button in the user panel has a red line through it, click it to undeafen yourself.',
    f'If a red microphone icon appears next to your name under the voice channel, ask a {T("moderator")} to unmute you. This icon means a moderator muted you for the whole server, and you cannot unmute yourself.',
    GEAR,
    f'Click {ui("Voice &amp; Video")} in the list on the left.',
    f'Under {ui("Voice &amp; Video")}, click {ui("Voice")}.',
    f'Open the {ui("Microphone")} menu.',
    'Click the microphone you are using.',
    f'If the {ui("Microphone Volume")} slider is low, drag it to the right.',
    f'If {ui("Input Mode")} is set to {ui("Push to Talk")}, then turn it off.',
    f'Click {ui("Mic Test")}.',
    'Speak into your microphone. If the bar moves and you hear yourself, your microphone works.',
    f'Click {ui("Stop Testing")}.',
)}
<p>If the bar did not move, Windows may be blocking Discord from using your microphone:</p>
{steps(
    f'Press {kbd("Windows")} + {kbd("I")} to open Windows Settings.',
    f'Click {ui("Privacy &amp; security")}.',
    f'Click {ui("Microphone")}.',
    f'Turn on {ui("Let desktop apps access your microphone")}. If Discord isn\'t automatically switched on, click the switch for Discord as well.',
)}
{result('Your group can hear you, and a green ring appears around your picture when you talk.')}
{note('If you run the Mic Test while you are in a voice channel, Discord mutes and deafens you until you click Stop Testing.')}
''',
    ('audio-video-problems.html', 'I Cannot Hear Others'): f'''
{steps(
    'If the headphone button in the user panel has a red line through it, click it.',
    "Right-click a teammate's name under the voice channel.",
    f'If the {ui("User Volume")} slider is all the way to the left, drag it to the right.',
    f'If {ui("Mute")} is checked, click it to uncheck it.',
    GEAR,
    f'Click {ui("Voice &amp; Video")} in the list on the left.',
    f'Open the {ui("Speaker")} menu.',
    'Click the speakers or headphones you are using.',
    f'If the {ui("Speaker Volume")} slider is low, drag it to the right.',
    'Click the speaker icon at the bottom-right of the Windows taskbar.',
    'If the volume is low or muted, drag the volume slider to the right.',
)}
{result('You can hear your teammates in the voice channel.')}
''',
    ('audio-video-problems.html', 'My Camera Will Not Turn On'): f'''
{steps(
    'Close other apps that may be using your camera, such as Zoom, Microsoft Teams, or the Windows Camera app.',
    GEAR,
    f'Click {ui("Voice &amp; Video")} in the list on the left.',
    f'Under {ui("Voice &amp; Video")}, click {ui("Camera")}.',
    f'Open the {ui("Camera")} menu.',
    'Click the camera you are using.',
    f'Click {ui("Test Video")} to check that your picture appears.',
)}
<p>If no picture appears, Windows may be blocking Discord from using your camera:</p>
{steps(
    f'Press {kbd("Windows")} + {kbd("I")} to open Windows Settings.',
    f'Click {ui("Privacy &amp; security")}.',
    f'Click {ui("Camera")}.',
    f'Turn on {ui("Camera access")}.',
    f'Turn on {ui("Let desktop apps access your camera")}.',
)}
<p>If the camera still does not work, restart Discord:</p>
{steps(
    'Right-click the Discord icon in the Windows notification area at the bottom-right of the taskbar.',
    f'Click {ui("Quit Discord")}.',
    'Open Discord again from the Start menu or your desktop.',
)}
{result('Your camera preview appears, and you can turn on your camera in the voice channel.')}
{caution('Clicking the X at the top-right of the Discord window does not fully close the app. Discord keeps running in the notification area, so use Quit Discord when a restart is needed.')}
''',
    # ---------------- 9.2 Channel and Invite Problems ----------------
    ('channel-invite-problems.html', 'I Cannot See a Channel'): f'''
{steps(
    f'If a {T("category")} name in the channel list has an arrow pointing right, click the name to show the channels under it.',
    'Click the server name at the top of the channel list.',
    f'If {ui("Hide Muted Channels")} is checked, click it to show muted channels again.',
    'Right-click the grayed-out channel.',
    f'Click {ui("Unmute Channel")}.',
)}
{result('The channel appears in your channel list.')}
{note(f'If the channel is still missing, ask a {T("moderator")} for help. You may need a {T("role")} that can see the channel. For example: "Hi, I am in Group 3. Could you give me the @Group 3 role so I can see our channel?"')}
''',
    ('channel-invite-problems.html', 'An Invite Link Does Not Work'): f'''
{steps(
    'Check the name in the user panel to make sure you are logged in to the right Discord account.',
    f'In Discord, click the plus button ({ui("Add a Server")}) in the server list.',
    f'Click {ui("Join a Server")}.',
    f'Copy the whole invite link again, and paste it into the {ui("Invite Link")} box. It should start with <strong>discord.gg/</strong> and have no spaces before or after it.',
    f'Click {ui("Join Server")}.',
    'If Discord says the invite is invalid or expired, ask your group for a new link that is set to never expire.',
)}
{result('The server opens, and its icon appears in your server list.')}
{note(f'A free Discord account can belong to up to 100 servers. If you reached that limit, right-click a server you no longer use, click {ui("Leave Server")}, and then try the invite again.')}
''',
    # ---------------- 9.3 Getting More Help ----------------
    ('getting-help.html', 'Asking Your Server for Help'): f'''
<p>A clear question with a screenshot gets answered faster. Follow these steps when this tutorial does not solve your problem.</p>
{steps(
    'Check the pinned messages in your server first. <a href="missed-messages.html">Subsection 5.3</a> shows how. Your group may have already posted the answer.',
    'Open the window that shows the problem.',
    f'Press {kbd("Windows")} + {kbd("Shift")} + {kbd("S")}, and then drag a box around the part of the screen that shows the problem. Windows copies the screenshot.',
    'Open the channel your server uses for questions, such as <strong>#help</strong> or <strong>#questions</strong>. If there is none, use the main chat channel.',
    'Type a short description: what you were trying to do, what happened, and what you already tried. For example: "I cannot hear anyone in Meeting Room. I already checked my Input/Output Device, and my headphones are not deafened."',
    f'Press {kbd("Ctrl")} + {kbd("V")} to add your screenshot to the message.',
    f'Press {kbd("Enter")}.',
    'When the problem is fixed, reply to say what worked, so the next person with the same problem can find the answer.',
)}
{result('Your question and screenshot appear in the channel, and teammates or moderators can reply with a fix.')}
{caution('Before posting a screenshot, check that it does not show private information, such as your email address, grades, or other open messages.')}
{note('For account problems your server cannot fix, such as a hacked account or a login error, visit the <a href="https://support.discord.com">Discord Help Center</a>.')}
''',
    ('meeting-etiquette.html', 'Before the Call'): '''<ul>
  <li>Review the project goals and agenda so everyone knows what needs to be discussed.</li>
  <li>Read any shared documents, messages, or updates before joining.</li>
  <li>Make sure your microphone, headphones, and internet connection are working properly.</li>
  <li>Join the call on time and be ready to participate.</li>
  <li>Prepare any questions, ideas, or progress updates you want to share.</li>
  <li>Close unnecessary apps or browser tabs that could distract you during the meeting.</li>
</ul>''',
    ('meeting-etiquette.html', 'During the Call'): '''<ul>
  <li>Mute your microphone when you are not speaking to reduce background noise.</li>
  <li>Listen carefully and avoid interrupting other group members.</li>
  <li>Stay focused on the project topic and avoid unrelated conversations.</li>
  <li>Use respectful language and give everyone a chance to contribute.</li>
  <li>Take notes on important decisions, tasks, and deadlines.</li>
  <li>Ask questions if something is unclear instead of making assumptions.</li>
  <li>Confirm action items before the meeting ends so everyone understands their responsibilities.</li>
  <li>Thank your teammates for their time and contributions before leaving the call.</li>
</ul>''',
    ('checklist.html', 'Core Skills Checklist'): '''<p>Check off each skill as you practice it. Your checks are not saved, so use this list as a quick review before your next group meeting.</p>
<h3>Server Navigation</h3>
<ul class="checklist">
  <li><label><input type="checkbox" id="ck1"> <span>Join a Discord server using an invite link.</span></label></li>
  <li><label><input type="checkbox" id="ck2"> <span>Identify categories and channels within a server.</span></label></li>
  <li><label><input type="checkbox" id="ck3"> <span>Navigate between text and voice channels.</span></label></li>
  <li><label><input type="checkbox" id="ck4"> <span>Locate important server information and announcements.</span></label></li>
</ul>
<h3>Communication</h3>
<ul class="checklist">
  <li><label><input type="checkbox" id="ck5"> <span>Send messages in a text channel.</span></label></li>
  <li><label><input type="checkbox" id="ck6"> <span>Reply to messages in a conversation.</span></label></li>
  <li><label><input type="checkbox" id="ck7"> <span>Use emoji reactions appropriately.</span></label></li>
  <li><label><input type="checkbox" id="ck8"> <span>Mention users with @mentions.</span></label></li>
  <li><label><input type="checkbox" id="ck9"> <span>Follow proper Discord etiquette when communicating.</span></label></li>
</ul>
<h3>Direct Messages &amp; Friends</h3>
<ul class="checklist">
  <li><label><input type="checkbox" id="ck10"> <span>Send a friend request.</span></label></li>
  <li><label><input type="checkbox" id="ck11"> <span>Accept or decline friend requests.</span></label></li>
  <li><label><input type="checkbox" id="ck12"> <span>Start and manage direct message conversations.</span></label></li>
  <li><label><input type="checkbox" id="ck13"> <span>Create and use group direct messages.</span></label></li>
</ul>
<h3>Voice &amp; Video Features</h3>
<ul class="checklist">
  <li><label><input type="checkbox" id="ck14"> <span>Join a voice channel.</span></label></li>
  <li><label><input type="checkbox" id="ck15"> <span>Mute and unmute your microphone.</span></label></li>
  <li><label><input type="checkbox" id="ck16"> <span>Deafen and undeafen yourself.</span></label></li>
  <li><label><input type="checkbox" id="ck17"> <span>Enable and disable your camera.</span></label></li>
  <li><label><input type="checkbox" id="ck18"> <span>Leave a voice channel correctly.</span></label></li>
</ul>
<h3>Screen Sharing &amp; Collaboration</h3>
<ul class="checklist">
  <li><label><input type="checkbox" id="ck19"> <span>Share your screen during a voice call.</span></label></li>
  <li><label><input type="checkbox" id="ck20"> <span>Select the correct application or window to share.</span></label></li>
  <li><label><input type="checkbox" id="ck21"> <span>Participate in study sessions or group discussions.</span></label></li>
  <li><label><input type="checkbox" id="ck22"> <span>Collaborate effectively during project meetings.</span></label></li>
</ul>
<h3>Account &amp; Profile Management</h3>
<ul class="checklist">
  <li><label><input type="checkbox" id="ck23"> <span>Update your username or display name.</span></label></li>
  <li><label><input type="checkbox" id="ck24"> <span>Modify your profile settings.</span></label></li>
  <li><label><input type="checkbox" id="ck25"> <span>Adjust notification preferences.</span></label></li>
  <li><label><input type="checkbox" id="ck26"> <span>Review Discord privacy and safety settings.</span></label></li>
</ul>
<h3>Organization &amp; Productivity</h3>
<ul class="checklist">
  <li><label><input type="checkbox" id="ck27"> <span>Use Discord to communicate with classmates.</span></label></li>
  <li><label><input type="checkbox" id="ck28"> <span>Participate in course-related servers.</span></label></li>
  <li><label><input type="checkbox" id="ck29"> <span>Follow channel rules and guidelines.</span></label></li>
  <li><label><input type="checkbox" id="ck30"> <span>Keep project discussions organized in appropriate channels.</span></label></li>
  <li><label><input type="checkbox" id="ck31"> <span>Use Discord professionally in academic environments.</span></label></li>
</ul>
''',
    ('beyond.html', 'Student Organizations and Future Classes'): f'''<p>Your group project is only the start. Student organizations and future classes at UCF may also invite you to a Discord server, and every skill you practiced here works the same way there.</p>
<h3>Finding a student organization</h3>
<p><a href="https://osi.ucf.edu/registered-student-organizations-rsos/get-involved/">KnightConnect</a> is UCF's official involvement platform, where you can explore over 600 Registered Student Organizations and view upcoming events. Each organization has its own page with meeting times, contact information, and ways to get involved. Log in with your NID and NID password to see every organization, as the <a href="https://osi.ucf.edu/rso/">Office of Student Involvement</a> explains.</p>
<p>If a club you join uses Discord, ask an officer for the invite link, and then join the server the same way you joined your group's server in <a href="accept-invite.html">Subsection 3.2</a>.</p>
<h3>Using your skills in a new server</h3>
<ul>
  <li><strong>Set a nickname:</strong> Use a <a href="server-nickname.html">server nickname</a> with your real name in class servers, and a different one in hobby clubs if you want.</li>
  <li><strong>Control your alerts:</strong> Clubs can be busy. Set each new server to <strong>Only @mentions</strong> in <a href="notifications.html">Subsection 6.1</a> so club chat does not bury class deadlines.</li>
  <li><strong>Read the rules first:</strong> Most servers have a rules or announcements channel. Read it before you post, just like you check pinned messages in <a href="missed-messages.html">Subsection 5.3</a>.</li>
  <li><strong>Use the same meeting habits:</strong> The etiquette in <a href="meeting-etiquette.html">Subsection 7.3</a> works for club meetings, study sessions, and officer calls.</li>
  <li><strong>Protect your privacy:</strong> Large servers include people you do not know. Keep the message and friend request limits from <a href="privacy-security.html">Subsection 6.2</a> turned on.</li>
</ul>
<h3>Future classes</h3>
<p>When a new professor or project group invites you to a Discord server, you do not need to start over. You already know how to join from an invite link, find the right channel, mention a teammate, share a file, and join a meeting. When a semester ends, you can leave servers you no longer need so your server list stays short and easy to read.</p>
''',
}

for f, intro in DRAFTS.items():
    sec = next((s for s in SECTIONS if s[1] == f), None)
    if sec:
        PAGES[f] = (intro, f'<p class="lead">{intro}</p>\n<p><strong>You need:</strong> {YOU_NEED[f]}</p>\n{overview(sec[0])}\n')
    else:
        body = f'<p class="lead">{intro}</p>\n'
        for h, kind in SCAFFOLD[f]:
            body += f'<h2>{h}</h2>\n' + (STEPS.get((f, h)) or (todo_steps() if kind == 'steps' else writing())) + '\n'
        PAGES[f] = (intro, body)

gloss = ''.join(
    f'<dt id="{re.sub(r"[^a-z0-9]+", "-", k.lower()).strip("-")}">{k[0].upper() + k[1:]}</dt><dd>{html.escape(v)}</dd>'
    for k, v in sorted(DEF.items(), key=lambda kv: kv[0].lower()))
PAGES['glossary.html'] = ('Plain-language definitions of every new Discord word in this tutorial.', f'''
<p class="lead">This glossary defines every new word in this tutorial in alphabetical order. The same definitions appear when you point to a blue word on any page.</p>
<dl class="glossary">{gloss}</dl>
''')

PAGES['final-conclusion.html'] = ('Congratulations on finishing the tutorial, plus official Discord help links for later.', f'''
<p class="lead">Congratulations, you've reached the end of this tutorial, and you are ready to use Discord with your class or group.</p>
<p>You can now create an account, join your group's server, find the right channels, send messages and files, control your notifications and privacy, join voice meetings, share your screen, and fix common problems on your own.</p>

<h2>More information in this tutorial</h2>
<ul>
  <li><a href="checklist.html">Subsection 8.1: Quick-Start Checklist</a>: Review every core skill in one list.</li>
  <li><a href="troubleshooting.html">Section 9: Troubleshooting Common Problems</a>: Find a fix by problem.</li>
  <li><a href="glossary.html">Section 11: Glossary</a>: Look up any new word from this tutorial.</li>
</ul>

<h2>Discord Help Center</h2>
<p>For anything this tutorial does not cover, visit the <a href="https://support.discord.com">Discord Help Center</a>. It is Discord's official support site, and you can search it for any feature, setting, or error message.</p>

<h2>Official Discord help links</h2>
<ul class="link-list">
  <li><a href="https://support.discord.com">Discord Help Center</a>: The official home of every Discord help article. Search it for any feature or error message.</li>
  <li><a href="https://support.discord.com/hc/en-us/articles/360045138571-Beginner-s-Guide-to-Discord">Beginner's Guide to Discord</a>: An overview of accounts, servers, text and voice channels, screen sharing, and profiles.</li>
  <li><a href="https://support.discord.com/hc/en-us/articles/215253258-Notifications-Settings-101">Notifications Settings 101</a>: Every server and channel notification option, including muting and @mention settings.</li>
  <li><a href="https://support.discord.com/hc/en-us/articles/219576828-Setting-up-Multi-Factor-Authentication">Setting up Multi-Factor Authentication</a>: How to protect your login with an authenticator app, passkeys, or security keys.</li>
  <li><a href="https://support.discord.com/hc/en-us/articles/360040816151-Go-Live-and-Screen-Share">Go Live and Screen Share</a>: How to share one window or your entire screen in a voice channel.</li>
  <li><a href="https://support.discord.com/hc/en-us/articles/360045138471-Discord-Voice-and-Video-Troubleshooting-Guide">Discord Voice and Video Troubleshooting Guide</a>: More fixes for microphone, speaker, and camera problems.</li>
  <li><a href="https://discord.com/safety/360043857751-four-steps-to-a-super-safe-account">Four Steps to a Safer Account</a>: Discord's Safety Center guide to passwords, privacy settings, and blocking.</li>
</ul>
''')

PAGES['credits.html'] = ('The sources and tools used to make this tutorial.', '''
<ul>
  <li><a href="https://support.discord.com">Discord Help Center</a> was used to verify any recent changes in button names, menus, or UIs.</li>
  <li>Both Discord accounts were made and used by Sebastian Foster for steps that require another user.</li>
  <li>Screenshots are original and were captured and annotated by Sebastian Foster with the Windows Snipping Tool and Google Drawings.</li>
  <li>The Discord Dark theme colors were obtained by copying hex codes from the appearance settings in the app. Other colors, including the green used for the title, the Table of Contents heading, and the section headings, were chosen by copying hex codes from Discord's Nitro color picker feature.</li>
</ul>
''')

# ---------------------------------------------------------------------------
# Write files
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    for f in glob.glob('*.html'):
        os.remove(f)
    for num, f, title, *_ in ORDER:
        entry = PAGES[f]
        desc, body = entry[0], entry[1]
        draft = len(entry) > 2 and entry[2]
        body = number_media(body, num)
        with open(f, 'w', encoding='utf-8') as fh:
            fh.write(page(f, body, desc, draft))
    # Old addresses from the first draft redirect to the new pages
    for old, new in {'create-account.html': 'getting-started.html', 'join-server.html': 'joining-a-server.html', 'what-is-discord.html': 'index.html', 'introduction.html': 'index.html'}.items():
        with open(old, 'w', encoding='utf-8') as fh:
            fh.write(f'<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta http-equiv="refresh" content="0; url={new}">'
                     f'<link rel="canonical" href="{new}"><title>Moved</title></head><body><p>This page moved to <a href="{new}">{new}</a>.</p></body></html>')
    print('Built', len(ORDER), 'pages')
