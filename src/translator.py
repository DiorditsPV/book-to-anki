import asyncio
from deep_translator import GoogleTranslator

async def translate_words(words, concurrency=10, source="en", target="ru"):
    semaphore = asyncio.Semaphore(concurrency)
    translations = {}

    async def translate_one(word):
        async with semaphore:
            return await asyncio.to_thread(
                lambda: GoogleTranslator(source=source, target=target).translate(word)
            )

    tasks = {word: asyncio.create_task(translate_one(word)) for word in words}
    for word, task in tasks.items():
        try:
            translations[word] = await task
        except Exception:
            translations[word] = None
    return translations

def translate_words_sync(words, concurrency=10, source="en", target="ru"):
    return asyncio.run(translate_words(words, concurrency=concurrency, source=source, target=target))
