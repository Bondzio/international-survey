#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Wrapper around survey_creation.py script to create only one survey file rather than separated ones as for 2016 and 2017 survey version
"""

__author__ = "Olivier Philippe"


import csv
from collections import OrderedDict


# # Here the list of the countries -- need to be put into a config file rather than hardcoded
# # TODO: config file!
dict_countries = {'de': "Germany",
                  'nl': "Netherlands",
                  'uk': "United Kingdom of Great Britain and Northern Ireland",
                  'us': "United States of America",
                  'zaf': "South Africa",
                  'nzl': "New Zealand",
                  'aus': "Australia",
                  'can': "Canada"}
list_bool = ['yes', 'y', 't', 'true']


class gettingQuestions:
    """
    This class parse the file `questions.csv` and create a dictionary with all the questions. It also parses all the specific countries folders and create a specific question for each of them when needed.
    """

    def __init__(self, *args, **kwargs):
        """
        """
        self.filename = "./2018/questions.csv"
        # Dictionary containing the different questions
        self.dict_questions = OrderedDict()

    def read_original_file(self):
        """
        load the file
        """
        with open(self.filename, "r") as f:
            csv_f = csv.DictReader(f)
            for row in csv_f:
                code = row['code']
                del row['code']
                self.dict_questions[code] = row

    def add_world_other(self):
        """
        Check question if it is country specific and one choice
        and if 'world' is also selected. In that case, add a new question
        using the same code and the same text but give a freetext and add the condition
        that should be NOT any country selected
        - create a new question with
            - code: '$code_world'
            - txt: '$txt_of_the_question' (just get the same text)
            - type: freetext
            - condition: (if not countries)
        """
        def check_world_free_txt(question):
            """
            Check if the question is  either one_choice or multiple_choice
            and its is selected as 'country_specific'
            and 'world' is selected then:
            :params:
                question dict(): the question to check
            :return:
                bool: True if match the condition, False if not
            """
            if question['country_specific'].lower() in list_bool:
                if question['world'].lower() in list_bool:
                    return True

        # recreate a new ordered dict
        new_dict = OrderedDict()
        # parse all the questions to find which one has to be created for world
        for k in self.dict_questions:
            # add the question to the new dict to respect the same order
            new_dict[k] = self.dict_questions[k]
            # check if the questions need to be created
            if check_world_free_txt(new_dict[k]):
                new_code = "{}_world".format(k)
                new_question = new_dict[k]
                new_question['answer_format'] = 'FREETEXT'
                new_question['answer_file'] = ''
                new_question['other'] = ''
                new_question['country_specific'] = ''
                for country in dict_countries:
                    new_question[country] = ''

                # append it to the dictionary
                new_dict[new_code] = new_question

        # replace the current dictionary with the new one
        self.dict_questions = new_dict

    def add_condition_about_countries(self):
        """
        Append the existing condition with the conditions about the countries
        """
        def create_country_list(question):
            """
            Check which country is associated with the question and
            return a list containing all of them. In case of `country_specific` is
            selected, it will not add the country `world` as a new specific question
            is created within self.add_world_other()
            params:
                question dict(): containing all the params for the question
            return:
                cond_country_to_add list(): all countries that are associated with the question
            """
            list_countries_to_add = list()
            for country in dict_countries:
                if question[country].lower() in list_bool:
                    list_countries_to_add.append(country)
            if question['world'].lower() in list_bool and question['country_specific'].lower() not in list_bool:
                list_countries_to_add.append('world')
            return list_countries_to_add

        def create_country_condition(country_code, operator="==", code_question_country="currentEmp1"):
            """
            Create the country condition based on the code of the country and the condition requested
            """
            return "(if {} {} {})".format(code_question_country, operator, code_question_country)

        for k in self.dict_questions:
            list_countries_to_add = create_country_list(self.dict_questions[k])
            # In case all the countries and world is present, no need to add any condition
            if len(list_countries_to_add) == len(dict_countries.keys()) +1:
                pass
            # In case only 'world' is present, need to add a NOT country for all countries
            elif 'world' in list_countries_to_add and len(list_countries_to_add) == 1:
                pass
            # Any other type, just add the list of country
            else:
                pass
            condition = self.dict_questions[k]['condition']


def main():
    getting_question = gettingQuestions()
    getting_question.read_original_file()
    getting_question.add_world_other()
    getting_question.add_condition_about_countries()
    # print(getting_question.dict_questions)


if __name__ == "__main__":
    main()
