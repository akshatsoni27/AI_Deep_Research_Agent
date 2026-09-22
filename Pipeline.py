import sys
import re
import time

from Agents import build_reader_agent , build_search_agent , writer_chain , critic_chain
from tools import scrape_urls


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def run_research_pipeline(topic : str) -> dict:

    state = {}

    #search agent working 
    print("\n"+" ="*50)
    print("step 1 - search agent is working ...")
    print("="*50)

    search_started = time.perf_counter()
    search_agent = build_search_agent()
    search_result = search_agent.invoke({
        "messages" : [("user", f"Find recent, reliable and detailed information about: {topic}")]
    })
    search_messages = search_result.get("messages", [])
    state["search_results"] = "\n\n".join(
        str(message.content)
        for message in search_messages
        if getattr(message, "content", None)
    )
    print(f"Search Agent: {time.perf_counter() - search_started:.2f}s")

    print("\n search result ",state['search_results'])

    #step 2 - reader agent 
    print("\n"+" ="*50)
    print("step 2 - Reader agent is scraping top resources ...")
    print("="*50)

    extraction_started = time.perf_counter()
    urls = re.findall(r"https?://[^\s)\]}>,]+", state["search_results"])
    urls = list(dict.fromkeys(urls))[:5]
    print(f"URL extraction: {time.perf_counter() - extraction_started:.2f}s")

    scrape_started = time.perf_counter()
    state["scraped_content"] = scrape_urls.invoke("\n".join(urls)) if urls else "No URLs found."
    print(f"Concurrent scraping: {time.perf_counter() - scrape_started:.2f}s")

    reader_started = time.perf_counter()
    reader_agent = build_reader_agent()
    reader_input = (
        f"Summarize the scraped sources for the topic '{topic}'.\n\n"
        f"Scraped content:\n{state['scraped_content'][:8000]}"
    )

    reader_result = reader_agent.invoke({
        "messages": [("user", reader_input)]
    })

    state['scraped_content'] = reader_result['messages'][-1].content
    print(f"Reader Agent: {time.perf_counter() - reader_started:.2f}s")

    print("\nscraped content: \n", state['scraped_content'])

    #step 3 - writer chain 

    print("\n"+" ="*50)
    print("step 3 - Writer is drafting the report ...")
    print("="*50)

    research_combined = (
        f"SEARCH RESULTS : \n {state['search_results'][:6000]} \n\n"
        f"DETAILED SCRAPED CONTENT : \n {state['scraped_content']}"
    )

    writer_started = time.perf_counter()
    state["report"] = writer_chain.invoke({
        "topic" : topic,
        "research" : research_combined
    })
    print(f"Writer Agent: {time.perf_counter() - writer_started:.2f}s")

    print("\n Final Report\n",state['report'])

    #critic report 

    print("\n"+" ="*50)
    print("step 4 - critic is reviewing the report ")
    print("="*50)

    critic_started = time.perf_counter()
    state["feedback"] = critic_chain.invoke({
        "report":state['report']
    })
    print(f"Critic Agent: {time.perf_counter() - critic_started:.2f}s")

    print("\n critic report \n", state['feedback'])

    return state



if __name__ == "__main__":
    topic = input("\n Enter a research topic : ")
    run_research_pipeline(topic)