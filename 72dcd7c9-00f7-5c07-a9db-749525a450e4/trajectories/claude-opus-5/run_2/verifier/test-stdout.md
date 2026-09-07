============================= test session starts ==============================
platform linux -- Python 3.11.16, pytest-9.1.1, pluggy-1.6.0 -- /usr/local/bin/python3
django: version: 4.2.30, settings: config.settings.test (from env)
rootdir: /home/dotmanca
configfile: pyproject.toml
plugins: django-4.14.0, env-1.7.0
collecting ... collected 33 items

dotmanca/users/tests/test_admin.py::test_clean_username_success PASSED   [  3%]
dotmanca/users/tests/test_admin.py::test_clean_username_false PASSED     [  6%]
dotmanca/users/tests/test_models.py::test__str__ PASSED                  [  9%]
dotmanca/users/tests/test_models.py::test_get_absolute_url PASSED        [ 12%]
dotmanca/users/tests/test_views.py::test_user_redirect_view_get_redirect_url PASSED [ 15%]
dotmanca/users/tests/test_views.py::test_user_update_view_get_success_url PASSED [ 18%]
dotmanca/users/tests/test_views.py::test_user_update_view_get_object PASSED [ 21%]
characters/tests.py::test_character_get_absolute_url_slug_appears_in_url PASSED [ 24%]
characters/tests.py::test_character_get_absolute_url_team_slug_appears_in_url PASSED [ 27%]
comics/tests.py::test_issue_get_absolute_url_slug_appears_in_url PASSED  [ 30%]
comics/tests.py::test_issue_get_absolute_url_arc_slug_appears_in_url PASSED [ 33%]
dotmanca/users/tests/test_urls.py::test_list_reverse PASSED              [ 36%]
dotmanca/users/tests/test_urls.py::test_list_resolve PASSED              [ 39%]
dotmanca/users/tests/test_urls.py::test_redirect_reverse PASSED          [ 42%]
dotmanca/users/tests/test_urls.py::test_redirect_resolve PASSED          [ 45%]
dotmanca/users/tests/test_urls.py::test_detail_reverse PASSED            [ 48%]
dotmanca/users/tests/test_urls.py::test_detail_resolve PASSED            [ 51%]
dotmanca/users/tests/test_urls.py::test_update_reverse PASSED            [ 54%]
dotmanca/users/tests/test_urls.py::test_update_resolve PASSED            [ 57%]
gallery/tests.py::test_gallery_get_absolute_url_slug_appears_in_url PASSED [ 60%]
gallery/tests.py::test_gallery_image_get_absolute_url_slug_appears_in_url PASSED [ 63%]
gallery/tests.py::test_gallery_image_get_absolute_url_gallery_slug_appears_in_url PASSED [ 66%]
main/tests.py::test_about_chas_view_age_in_context_of_about PASSED       [ 69%]
main/tests.py::test_about_chas_view_age_ten_years_after_birthday_is_ten PASSED [ 72%]
main/tests.py::test_about_chas_view_age_ten_years_minus_one_day_after_birthday_is_nine_about PASSED [ 75%]
main/tests.py::test_about_evan_view_context_contains_age PASSED          [ 78%]
main/tests.py::test_about_evan_view_age_ten_years_after_birthday_is_ten PASSED [ 81%]
main/tests.py::test_about_evan_view_age_ten_years_minus_one_day_after_birthday_is_nine PASSED [ 84%]
main/tests.py::test_context_contains_news_articles PASSED                [ 87%]
main/tests.py::test_context_contains_only_three_news_articles_when_4_come_back PASSED [ 90%]
news/tests.py::test_news_article_get_absolute_url_date_appears_in_url PASSED [ 93%]
news/tests.py::test_news_article_get_absolute_url_slug_appears_in_url PASSED [ 96%]
places/tests.py::test_place_get_absolute_url_slug_appears_in_url PASSED  [100%]

==================================== PASSES ====================================
_________________________ test_clean_username_success __________________________
---------------------------- Captured stderr setup -----------------------------
Creating test database for alias 'default'...
--------------------------- Captured stderr teardown ---------------------------
Destroying test database for alias 'default'...
=========================== short test summary info ============================
PASSED dotmanca/users/tests/test_admin.py::test_clean_username_success
PASSED dotmanca/users/tests/test_admin.py::test_clean_username_false
PASSED dotmanca/users/tests/test_models.py::test__str__
PASSED dotmanca/users/tests/test_models.py::test_get_absolute_url
PASSED dotmanca/users/tests/test_views.py::test_user_redirect_view_get_redirect_url
PASSED dotmanca/users/tests/test_views.py::test_user_update_view_get_success_url
PASSED dotmanca/users/tests/test_views.py::test_user_update_view_get_object
PASSED characters/tests.py::test_character_get_absolute_url_slug_appears_in_url
PASSED characters/tests.py::test_character_get_absolute_url_team_slug_appears_in_url
PASSED comics/tests.py::test_issue_get_absolute_url_slug_appears_in_url
PASSED comics/tests.py::test_issue_get_absolute_url_arc_slug_appears_in_url
PASSED dotmanca/users/tests/test_urls.py::test_list_reverse
PASSED dotmanca/users/tests/test_urls.py::test_list_resolve
PASSED dotmanca/users/tests/test_urls.py::test_redirect_reverse
PASSED dotmanca/users/tests/test_urls.py::test_redirect_resolve
PASSED dotmanca/users/tests/test_urls.py::test_detail_reverse
PASSED dotmanca/users/tests/test_urls.py::test_detail_resolve
PASSED dotmanca/users/tests/test_urls.py::test_update_reverse
PASSED dotmanca/users/tests/test_urls.py::test_update_resolve
PASSED gallery/tests.py::test_gallery_get_absolute_url_slug_appears_in_url
PASSED gallery/tests.py::test_gallery_image_get_absolute_url_slug_appears_in_url
PASSED gallery/tests.py::test_gallery_image_get_absolute_url_gallery_slug_appears_in_url
PASSED main/tests.py::test_about_chas_view_age_in_context_of_about
PASSED main/tests.py::test_about_chas_view_age_ten_years_after_birthday_is_ten
PASSED main/tests.py::test_about_chas_view_age_ten_years_minus_one_day_after_birthday_is_nine_about
PASSED main/tests.py::test_about_evan_view_context_contains_age
PASSED main/tests.py::test_about_evan_view_age_ten_years_after_birthday_is_ten
PASSED main/tests.py::test_about_evan_view_age_ten_years_minus_one_day_after_birthday_is_nine
PASSED main/tests.py::test_context_contains_news_articles
PASSED main/tests.py::test_context_contains_only_three_news_articles_when_4_come_back
PASSED news/tests.py::test_news_article_get_absolute_url_date_appears_in_url
PASSED news/tests.py::test_news_article_get_absolute_url_slug_appears_in_url
PASSED places/tests.py::test_place_get_absolute_url_slug_appears_in_url
============================== 33 passed in 0.43s ==============================
