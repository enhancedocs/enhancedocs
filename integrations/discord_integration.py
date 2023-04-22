import os
import discord
import main
import utils
from langchain import PromptTemplate
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.chains import RetrievalQAWithSourcesChain


class DiscordClient(discord.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')

    async def on_message(self, message):
        if message.author.id == self.user.id:
            return

        mention = f'<@{self.user.id}>'
        if message.content.startswith(mention):
            if isinstance(message.channel, discord.Thread):
                async for msg in message.channel.history(oldest_first=True):
                    print(f"{msg.author}: {msg.content}")
                return
            question = message.content.split(f'{mention} ', 1)[1]
            thread = await message.create_thread(name=question)
            async with thread.typing():
                store = utils.get_vector_store(main.config)
                prompt = PromptTemplate(
                    template=main.config.prompt_template, input_variables=["summaries", "question", "project_name"]
                )
                qa_chain = load_qa_with_sources_chain(main.llm, chain_type="stuff", prompt=prompt)
                chain = RetrievalQAWithSourcesChain(
                    combine_documents_chain=qa_chain,
                    retriever=store.as_retriever(),
                    return_source_documents=True
                )
                result = chain(
                    {"question": question, "project_name": main.config.project_name},
                    return_only_outputs=True
                )
                await thread.send(content=result["answer"], mention_author=True)


async def start():
    intents = discord.Intents.default()
    intents.message_content = True

    client = DiscordClient(intents=intents)
    try:
        await client.start(os.environ.get("DISCORD_TOKEN"))
    except KeyboardInterrupt:
        await client.close()
