from bot.config import uniq_text_auto_pars


def search_and_replace(
        content: str,
        replace: bool = False,
) -> str | bool:
    if (uniq_text_auto_pars in content) and replace:
        return content.replace(uniq_text_auto_pars, "")

    elif uniq_text_auto_pars in content:
        return True

    return False
