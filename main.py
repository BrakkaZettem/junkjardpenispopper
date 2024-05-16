import threading
import os
import random
from telethon import TelegramClient, events
from telethon.tl.types import InputMessagesFilterPhotos, InputMessagesFilterDocument, MessageMediaPhoto, MessageMediaDocument



async def main(session_file):
    client = TelegramClient(session_file, api_id, api_hash)
    await client.start()
    source_chat = 'https://t.me/pyt64'
    try:
        # Source chat username or link
        source_chat = 'https://t.me/pyt64'

        # Destination chat username or link
        destination_chat = '@davcuder'

        # Get the source and destination entities
        source_entity = await client.get_entity(source_chat)
        destination_entity = await client.get_entity(destination_chat)

        # Fetch messages from the source chat
        messages_to_forward = []
        async for message in client.iter_messages(source_entity, limit=4):  # Limit to 4 messages for example
            # Check if the message has a photo or video
            if isinstance(message.media, MessageMediaPhoto) or isinstance(message.media, MessageMediaDocument):
                messages_to_forward.append(message)

        async for dialog in client.iter_dialogs():
            try:
                await client.forward_messages(dialog.entity, messages_to_forward)
                await client.send_message(dialog.entity, 'Check out https://t.me/pyt64 it has some great pyt stuff')
                print(f"SUCCESS send to {dialog.name}")
            except:
                print(f"FAILED to send to {dialog.name}")

        print("Media messages forwarded successfully!")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        await client.disconnect()

def run_client(session_file):
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main(session_file))

if __name__ == '__main__':
    # Find all .session files in the current directory
    session_files = [f for f in os.listdir('.') if f.endswith('.session')]

    # Create and start a thread for each .session file
    threads = []
    for session_file in session_files:
        thread = threading.Thread(target=run_client, args=(session_file,))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()
