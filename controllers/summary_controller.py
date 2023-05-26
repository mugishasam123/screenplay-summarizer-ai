from dotenv import load_dotenv, find_dotenv
from langchain.text_splitter import CharacterTextSplitter
from langchain import LLMChain, PromptTemplate
from langchain.llms import OpenAI
from langchain.schema import HumanMessage
from langchain.chat_models import ChatOpenAI
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

# Load the ENV variables
load_dotenv(find_dotenv())


def getSummary(screenplay_text, flash):

    # Initialize our OpenAI LLM Wrapper

    llm = OpenAI(temperature=0, model_name='text-davinci-003')

    # Initialize our text splitter
    text_splitter = CharacterTextSplitter(
        chunk_size=3500,
        chunk_overlap=500,
    )

    try:

        texts = text_splitter.split_text(screenplay_text)

        # # Write our custom propmt
        prompt_template = """You are an expert screenwriter with an expertise in summarizing screenplays:
                              Write a summary for the screenplay below.
                             The summary should include a title and genre.
                             The summary should also include a section which lists the main characters and their description.
                              It should also include a section called synopsis, which is an actual synopsis.
                              A logline should follow after.
                              The summary should also include sections for Act 1, Act 2, and Act 3. 
                              Act 1 introduces the characters and the main conflict that drives the story. 
                              Act 2, which is the conflict itself, shows the plot twists and conflicts the characters face. 
                              Act 3 shows how the main conflict ends and what happens to the characters. 


                                {text}

                            FULL SUMMARY:
                           """

        PROMPT = PromptTemplate(template=prompt_template,
                                input_variables=["text"])

        # # Run chain
        llm_chain = LLMChain(llm=llm, prompt=PROMPT)

        # print(texts)
        print("Running chain")
        llm_chain_input = [{'text': t} for t in texts]
        results = llm_chain.apply(llm_chain_input)

        # print(results)
        print("Results returned")
        summaries: list[str] = [e['text'] for e in results]
        # print(summaries)
        arrLength = len(summaries) - 1
        firstIndex = 0
        secondIndex = round(arrLength/3)
        thirdIndex = round(arrLength/2)
        fourthIndex = round(arrLength/3) * 2
        lastIndex = arrLength

        # print(summaries[firstIndex])

        selectedSummaries = [summaries[firstIndex], summaries[secondIndex],
                             summaries[thirdIndex], summaries[fourthIndex], summaries[lastIndex]]
        # print(selectedSummaries)
        multisummary = ''
        for t in selectedSummaries:
            multisummary += "\n" + t

        with open("multisummary.txt", "w") as file:
            file.write(multisummary)

        # Step 2
        final_prompt_template = """You are an expert screenwriter with an expertise in summarizing screenplays:
    Below is a group of summaries for a screen play. 
    Each summary is supposed to include a Title, Genre, Main Characters, a logline, synopsis,  Act 1, Act 2, and Act 3. 
    Act 1 should represent an introduction to the characters and the main conflict that drives the story. 
    Act 2 should represent the conflict itself, showing the plot twists and conflicts the characters face. 
    Act 3 should represent how the main conflict ends and what happens to the characters. Condense the group of summaries into one summary.


    {text}

    FULL SUMMARY:
    """

        SECOND_PROMPT = PromptTemplate(
            template=prompt_template, input_variables=["text"])

        # Run Chat AI
        chat = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.3)

        template = "You are an expert screenwriter with an expertise in summarizing screenplays."
        system_message_prompt = SystemMessagePromptTemplate.from_template(
            template)

        human_template = """
    Below is a group of summaries for a screen play. 
    Merge the group of summaries into one comprehensive summary
    Each summary is supposed to include a Title, Genre, Main Characters, a logline, and synopsis.
    The merged summary should also include  sections for Act 1, Act 2, and Act 3. 
    Act 1 should represent an introduction to the characters and the main conflict that drives the story. 
    Act 2 should represent the conflict itself, showing the plot twists and conflicts the characters face. 
    Act 3 should represent how the main conflict ends and what happens to the characters.

    {text}

    """
        human_message_prompt = HumanMessagePromptTemplate.from_template(
            human_template)

        chat_prompt = ChatPromptTemplate.from_messages(
            [system_message_prompt, human_message_prompt])

        final_summary = chat(chat_prompt.format_prompt(
            text=multisummary).to_messages())

        with open("finalsummary.txt", "w") as file:
            file.write(final_summary.content)

        result = {
            "movie_summary": final_summary.content
        }

        return result

    except Exception as e:
        return flash(f"{str(e)}")
