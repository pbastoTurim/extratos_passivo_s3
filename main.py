from src.bot.extractor import  S3Extractor

bot = S3Extractor()
bot.login()
bot.navega_passivo()
bot.download()
input("Pressione Enter para sair...")