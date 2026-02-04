const { default: makeWASocket, useMultiFileAuthState, makeCacheableSignalKeyStore, Browsers, delay } = require("@whiskeysockets/baileys");
const pino = require("pino");
const { exec } = require("child_process");
const fs = require("fs");
const readline = require("readline");

// Terminal Colors
const Green = "\x1b[32m";
const Red = "\x1b[31m";
const Reset = "\x1b[0m";

const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
const question = (q) => new Promise((resolve) => rl.question(q, resolve));

async function mainSystem() {
    console.clear();

    // 1. طباعة شعار الطير باللون الأخضر
    console.log(Green + `⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣀⣀⣀⣀⣠⣼⠂⠀⠀⠀⠀⠙⣦⢀⠀⠀⠀⠀⠀⢶⣤⣀⣀⣀⣀⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣴⣶⣿⣿⣿⣿⣿⣿⣿⣿⠷⢦⠀⣹⣶⣿⣦⣿⡘⣇⠀⠀⠀⢰⠾⣿⣿⣿⣟⣻⣿⣿⣿⣷⣦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣤⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⠀⠀⠀⠀⢺⣿⣿⣿⣿⣿⣿⣿⣆⠀⠀⠀⠀⠀⠀⢹⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⢟⣥⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⢻⣿⣿⡏⢹⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣮⣝⢷⣄⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⢛⣿⣿⣿⡇⠀⠀⠀⠀⠛⣿⣿⣷⡀⠘⢿⣧⣻⡷⠀⠀⠀⠀⠀⠀⣿⣿⣿⣟⢿⣿⣿⣿⣿⣿⣿⣿⣿⣝⢧⡀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢠⣾⣿⠟⣡⣾⣿⣿⣧⣿⡿⣋⣴⣿⣿⣿⣿⣧⠀⠀⠀⠀⠀⢻⣿⣿⣿⣶⡄⠙⠛⠁⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⣷⣝⢻⣿⣟⣿⣿⣷⣮⡙⢿⣽⣆⠀⠀⠀⠀⠀
⠀⠀⠀⠀⢀⡿⢋⣴⣿⣿⣿⣿⣿⣼⣯⣾⣿⣿⡿⣻⣿⣿⣿⣦⠀⠀⠀⠀⢀⣹⣿⣿⣿⣿⣶⣤⠀⠀⠀⠀⠀⣰⣿⣿⣿⣿⠻⣿⣿⣿⣮⣿⣿⣿⣿⣿⣿⣦⡙⢿⣇⠀⠀⠀⠀
⠀⠀⠀⣠⡏⣰⣿⣿⡿⢿⣿⣿⣿⣿⣿⣿⡿⢋⣼⣿⣿⣿⣿⣿⣷⡤⠀⣠⣿⣿⣿⣿⣿⣿⣿⣿⣷⣄⠀⢠⣾⣿⣿⣿⣿⣿⣷⡜⢿⣿⣿⣿⣿⣿⣿⡿⠿⣿⣿⣦⡙⣦⠀⠀⠀
⠀⠀⣰⢿⣿⣿⠟⠋⣠⣾⣿⣿⣿⣿⣿⠛⢡⣾⡿⢻⣿⣿⣿⣿⣿⣿⣿⣿⡿⠋⠻⣿⡟⣿⣿⣿⠻⢿⣿⣿⣿⣿⣿⣿⣿⣟⠻⣿⣆⠙⢿⣿⣿⣿⣿⣿⣦⡈⠻⣿⣿⣟⣧⠀⠀
⠀⣰⢣⣿⡿⠃⣠⡾⠟⠁⠀⣸⣿⡟⠁⢀⣿⠋⢠⣿⡏⣿⣿⣿⣿⣿⢿⠁⢀⣠⣴⢿⣷⣿⣿⣿⠀⠀⠽⢻⣿⣿⣿⣿⡼⣿⡇⠈⢿⡆⠀⠻⣿⣧⠀⠈⠙⢿⣆⠈⠻⣿⣎⢧⠀
⠀⢣⣿⠟⢀⡼⠋⠀⠀⢀⣴⠿⠋⠀⠀⣾⡟⠀⢸⣿⠙⣿⠃⠘⢿⡟⠀⣰⢻⠟⠻⣿⣿⣿⣿⣿⣀⠀⠀⠘⣿⠋⠀⣿⡇⣿⡇⠀⠸⣿⡄⠀⠈⠻⣷⣄⠀⠀⠙⢷⡀⠙⣿⣆⠁
⢀⣿⡏⠀⡞⠁⢀⡠⠞⠋⠁⠀⠀⠀⠈⠉⠀⠀⠀⠿⠀⠈⠀⠀⠀⠀⠀⣿⣿⣰⣾⣿⣿⣿⣿⣿⣿⣤⠀⠀⠀⠀⠀⠉⠀⠸⠃⠀⠀⠈⠋⠀⠀⠀⠀⠙⠳⢤⣀⠀⠹⡄⠘⣿⡄
⣸⡟⠀⣰⣿⠟⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠛⠿⠿⠿⠟⠁⠀⠹⣿⣷⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⣿⣧⠀⢹⣷
⣿⠃⢠⡿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣄⣤⣀⠀⠀⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢻⡇⠀⣿
⣿⠀⢸⠅⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⡿⠋⠉⢻⣧⢀⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⠀⢸
⡇⠀⠈⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢿⣧⡀⠀⠀⣿⣾⡟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠀⢸
⢸⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⠿⣿⣿⠟⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡾
⠈⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⡿⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠃` + Reset);

    // 2. طباعة الاسم باللون الأحمر
    console.log(Red + ` __  __       _                                        _
|  \\/  | ___ | |__   __ _ _ __ ___  _ __ ___   ___  __| |
| |\\/| |/ _ \\| '_ \\ / _\` | '_ \` _ \\| '_ \` _ \\ / _ \\/ _\` |
| |  | | (_) | | | | (_| | | | | | | | | | |  __/ (_| |
|_|  |_|\\___/|_| |_|\\__,_|_| |_| |_|_| |_| |_|\\___|\\__,_|` + Reset);

    console.log("\n" + Green + "-----------------------------------------" + Reset);
    console.log("       Legend Development System       ");
    console.log(Green + "-----------------------------------------" + Reset);
    console.log("1 - Search for Session (Use current)");
    console.log("2 - Create New Session (New Pairing)");
    console.log(Green + "-----------------------------------------" + Reset);

    const choice = await question("📩 Choice: ");

    if (choice === "2") {
        if (fs.existsSync("session_dff")) {
            fs.rmSync("session_dff", { recursive: true, force: true });
            console.log(Red + "⚠️ Old session deleted." + Reset);
        }
    }

    startBot();
}

async function startBot() {
    const { state, saveCreds } = await useMultiFileAuthState("session_dff");

    const sock = makeWASocket({
        logger: pino({ level: "silent" }),
        auth: {
            creds: state.creds,
            keys: makeCacheableSignalKeyStore(state.keys, pino({ level: "silent" }))
        },
        browser: Browsers.ubuntu("Chrome"),
        markOnlineOnConnect: true
    });

    if (!sock.authState.creds.registered) {
        console.log(Green + "\n--- 🌟 PAIRING SYSTEM STARTING ---" + Reset);
        let phone = await question("📱 Enter WhatsApp Number (Example: 967xxxxxxxx): ");
        phone = phone.replace(/[+ ]/g, "");

        await delay(3000); // تسريع الانتظار
        try {
            const code = await sock.requestPairingCode(phone);
            console.log(Green + `\n✅ YOUR PAIRING CODE: ` + Red + code + Reset);
        } catch {
            console.log(Red + "❌ Pairing failed" + Reset);
            process.exit();
        }
    }

    sock.ev.on("creds.update", saveCreds);

    sock.ev.on("connection.update", ({ connection }) => {
        if (connection === "open")
            console.log(Green + "\n🎊 CONNECTED SUCCESSFULLY! Bot is active ✅" + Reset);

        if (connection === "close") {
            console.log(Red + "🔄 Connection lost, restarting..." + Reset);
            setTimeout(startBot, 5000);
        }
    });

    sock.ev.on("messages.upsert", async ({ messages }) => {
        const msg = messages[0];
        if (!msg.message || msg.key.fromMe) return;

        const text =
            msg.message.conversation ||
            msg.message.extendedTextMessage?.text ||
            msg.message.imageMessage?.caption ||
            "";

        const from = msg.key.remoteJid;

        const platforms = [
            "tiktok.com",
            "facebook.com",
            "fb.watch",
            "youtube.com",
            "youtu.be",
            "instagram.com",
            "pinterest.com",
            "pin.it"
        ];

        if (!platforms.some(p => text.includes(p))) return;

        let platform = "الفيديو";
        if (text.includes("tiktok")) platform = "تيك توك";
        else if (text.includes("facebook") || text.includes("fb.watch")) platform = "فيسبوك";
        else if (text.includes("youtube") || text.includes("youtu.be")) platform = "يوتيوب";
        else if (text.includes("instagram")) platform = "انستقرام";
        else if (text.includes("pinterest") || text.includes("pin.it")) platform = "بينترست";

        await sock.sendMessage(from, {
            text: `*جاري سحب فيديو ${platform}  ✅*`
        });

        const file = `video_${Date.now()}.mp4`;

        // تحميل الفيديو + دمج الصوت تلقائي + ترميز mp4 متوافق مع واتساب
        const cmd = `
yt-dlp -f "bestvideo[ext=mp4][vcodec^=avc]+bestaudio[ext=m4a]/best[ext=mp4]/best" \
--merge-output-format mp4 --no-playlist --no-check-certificate \
--recode-video mp4 -o "${file}" "${text}"
        `;

        exec(cmd, async (err) => {
            if (err || !fs.existsSync(file)) {
                return sock.sendMessage(from, { text: `❌ فشل تحميل فيديو من ${platform}.` });
            }

            // إرسال الفيديو بعد التأكد من التوافق
            await sock.sendMessage(from, {
                video: fs.readFileSync(file),
                caption: `*تم التحميل بواسطة الأسطورة ✅*`,
                mimetype: "video/mp4"
            });

            if (fs.existsSync(file)) fs.unlinkSync(file);
        });
    });
}

mainSystem();