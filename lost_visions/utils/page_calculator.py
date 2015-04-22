__author__ = 'ubuntu'


def get_page_multipliers(total_number_of_pages, current_page):
    page_multiplier = total_number_of_pages
    tens_count = 0
    buttons = []
    while page_multiplier > 0:
        if page_multiplier % 10 > 0:
            if total_number_of_pages - (10 ** tens_count) > current_page:
                buttons.append({
                    'text': '+' + str(10 ** tens_count),
                    'page': (10 ** tens_count) + current_page
                })

            if current_page - (10 ** tens_count) > 0:
                buttons.insert(0, {
                    'text': -(10 ** tens_count),
                    'page': current_page - (10 ** tens_count)
                })

            tens_count += 1
            page_multiplier /= 10
    return buttons