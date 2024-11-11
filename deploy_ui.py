import streamlit as st
from streamlit_chat import message
from rag import ChatNews

from crawl import get_category_link, get_news_links, load_doc


st.set_page_config(page_title="ChatNews")
category_links = get_category_link()


def display_messages():
    st.subheader("Chat")
    for i, (msg, is_user) in enumerate(st.session_state["messages"]):
        message(msg, is_user=is_user, key=str(i))
    st.session_state["thinking_spinner"] = st.empty()


def process_input():
    if (
        st.session_state["user_input"]
        and len(st.session_state["user_input"].strip()) > 0
    ):
        user_text = st.session_state["user_input"].strip()
        print(user_text)

        with st.session_state["thinking_spinner"], st.spinner("Thinking"):
            agent_text = st.session_state["assistant"].ask(user_text)

        st.session_state["messages"].append((user_text, True))
        st.session_state["messages"].append((agent_text, False))


def query(pages):
    for category in st.session_state["selected_categories"]:
        print(category)
        if category not in st.session_state["assistant"].saved_doc_categories:
            links = get_news_links(category_links[category], pages)
            docs = load_doc(links, category)
            st.session_state["assistant"].ingest(docs, category)


def reset():
    st.session_state["assistant"].clear()
    st.session_state["messages"] = []
    st.session_state["user_input"] = ""
    st.session_state["selected_categories"] = []
    st.session_state["num_news"] = 50


def page():
    if len(st.session_state) == 0:
        st.session_state["messages"] = []
        st.session_state["assistant"] = ChatNews()

    st.header("ChatNews")
    default_catetgory = "Latest"
    st.subheader("I will read some news about these topics from thenextweb.com")
    st.multiselect(
        "Select some topic that you are interested in",
        category_links.keys(),
        [default_catetgory],
        key="selected_categories",
    )
    st.number_input(
        "Number of news to read", min_value=10, value=50, step=10, key="num_news"
    )
    _, _, left, right = st.columns(4)
    left.button(
        "Read",
        on_click=query,
        kwargs={"pages": st.session_state["num_news"] // 10},
        use_container_width=True,
    )
    right.button("Reset", on_click=reset, use_container_width=True)
    st.session_state["ingestion_spinner"] = st.empty()
    display_messages()
    st.text_input("Message", key="user_input", on_change=process_input)


if __name__ == "__main__":
    page()
