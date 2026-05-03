from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.language_models import BaseChatModel


SYSTEM_PROMPT = """\
You are a skilled author writing in the {genre} genre.
{style_notes}
{writing_style_note}
{universe_note}
Book: {title}
Premise: {premise}

Characters (Main characters appear throughout and drive the story; Central characters \
are significant figures who may appear or disappear but carry their own history and voice):
{characters}

{previous_context}\
"""

HUMAN_PROMPT = """\
Write Chapter {chapter_number}: {chapter_title}

Summary: {chapter_summary}

Scenes to cover:
{scenes}

Write the full chapter in prose. Do not include the chapter heading.\
"""


def build_chapter_chain(llm: BaseChatModel):
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", HUMAN_PROMPT),
    ])
    return prompt | llm | StrOutputParser()
