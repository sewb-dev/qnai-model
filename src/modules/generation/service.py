import uuid
from openai import AsyncOpenAI
from src.settings import settings
from src.cache import get_cache
from src.enums import GenerationStatus
import calendar
from datetime import datetime, timedelta

client = None


class GenerationService:
    def prompt(
        self,
        sourceText: str,
        numberOfQuestions=10,
    ):
        return f"""
    Generate a set of ${numberOfQuestions} difficult educational questions and answers from the following text. I want to use these questions to prepare an examination for my students. Please format the questions and answers as JSON and wrap the JSON response with specific characters for easy parsing in code. Format each question as a question object which comprises of the following five properties;

    1. Question Number. Call this property 'id'. Its value should be the question number
    2. Question Type. Call this property 'type'. Its value should be the type of question. There are two possible question types, namely 'trueOrFalse' and 'multipleChoice'
    3. Question. Call this property 'question'. Its value should be the question that the student has to answer based on the text. If the 'type' is 'trueOrFalse', then the value of the 'q' should be a question that students can answer either 'True' or 'False' to. If the 'type' is 'multipleChoice', then the value of the 'q' should be a question that has only one correct answer from a list of options.
    3. Options. Call this property 'options'. Its value should be a list of string options available for my students to pick from.  If the 'type' is 'trueOrFalse', the options should be 'True' and 'False' because those are the only options available to my students. If the 'type' is 'multipleChoice', the options should be a list of the options my students have to pick from. I want four options only.
    4. Answer. Call this property 'answers'. Its value should be the correct answer to the question. The value should be the zero-based index of the correct answer in the list of 'options'.
    5. Context. Call this property 'context'. Its value should be the specific portion of the text that contains the answer to the question. It must read word for word from the text.

    It is important that you add these five properties to each of the question objects. It is equally important that 70% of the questions are of type 'multipleChoice', and '30%' are of type 'trueOrFalse'. Also, ensure that the questions and answers are relevant to the text, and that the answer is correct. Return a JSON object that has one key named questions and the value is a list of question objects with the five previously named properties. Here is the relevant text:

    '''
    ${sourceText}
    '''

    """

    def generation_id(self):
        return uuid.uuid4()

    async def generate(self, text: str, numberOfQuestions, generationId: str):
        key = f"{settings.GENERATION_JOB_PREFFIX_KEY}:{generationId}"
        global client
        if not client:
            client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        cache = await get_cache()

        content = ""

        generation_dict = {
            "status": GenerationStatus.INCOMPLETE.value,
            "content": content,
            "error": None,
            "prompt": self.prompt(text, numberOfQuestions),
        }

        try:
            stream = await client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a world class Question Generator",
                    },
                    {
                        "role": "user",
                        "content": self.prompt(text, numberOfQuestions),
                    },
                ],
                stream=True,
                model="gpt-3.5-turbo-1106",
                response_format={"type": "json_object"},
            )

            async for part in stream:
                print(part.choices[0].delta.content or "")
                content += part.choices[0].delta.content or ""
                generation_dict["content"] = content

                await cache.json().set(
                    key,
                    "$",
                    generation_dict,
                )
            generation_dict["status"] = GenerationStatus.COMPLETE.value
            generation_dict["content"] = content

            await cache.json().set(
                key,
                "$",
                generation_dict,
            )

        except Exception as e:
            generation_dict["status"] = GenerationStatus.COMPLETE.value
            generation_dict["content"] = None
            generation_dict["error"] = e

            await cache.json().set(
                key,
                "$",
                generation_dict,
            )
            print(e)

        finally:
            await cache.expireat(
                key,
                self.__get_session_expiry(settings.DELETE_GENERATION_AFTER_DAYS),
            )

    async def generation_status(self, generationId: str):
        try:
            cache = await get_cache()
            data = await cache.json().get(
                f"{settings.GENERATION_JOB_PREFFIX_KEY}:{generationId}"
            )

            if data["status"] == GenerationStatus.INCOMPLETE.value:
                data["content"] = None
            del data["prompt"]

            return data
        except Exception as e:
            response = {
                "status": GenerationStatus.INCOMPLETE.value,
                "content": None,
                "error": None,
            }
            print(e)
            response["status"] = GenerationStatus.COMPLETE.value
            response["error"] = e
            return response

    def __get_session_expiry(self, days: int) -> int:
        current_datetime = datetime.now()
        if days < 1:
            hours = round(days * 24, 1)
            days = 0
        else:
            hours = 0
        expiry_datetime = current_datetime + timedelta(days=days, hours=hours)
        return calendar.timegm(expiry_datetime.timetuple())


generation_settings = GenerationService()
