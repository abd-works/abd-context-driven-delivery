# Agent tool examples

## read_card — load the quick-start card

Called `read_card("quick-start")`. AssetLocator resolved `quick-start.md` beside
the class and Asset returned its full content.

## read_all — load every card in the cards/ folder

Called `read_all()`. AssetCollection found `cards/` and merged all `.md` files
inside it into one response.

## set_topic then read_card

Called `set_topic("faq")` to switch the default topic, then confirmed the topic
resource updated before calling `read_card("faq")`.
