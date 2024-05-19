import csv
import json
import re
import itertools
from pathlib import Path
from unicodedata import normalize

import pandas as pd
from tqdm import tqdm
from bs4 import BeautifulSoup, ResultSet, Tag
from pydantic import TypeAdapter

from src.pipeline_afsa_publicreg.utils import (
    get_response,
    base_url,
    normalize_tag,
)

from src.pipeline_afsa_publicreg.schemas import (
    LanguageType,
    Status,
    Organization,
    OrganizationName,
    OrganizationAddress,
    OrganizationActivity,
    OrganizationRole,
    OrganizationShareClasses,
    OrganizationCollateralInformation,
    OrganizationShareholders,
    OrganizationLicense,
    OrganizationLicenseIndividual,
)

base_url = "https://publicreg.myafsa.com/"

def get_categories_links_json():
    response = get_response(url=base_url)
    
    with open("../extracted_data/afsa_publicreg/categories.html", "w", encoding="utf-8") as file:
        file.write(response)

    with open("../extracted_data/afsa_publicreg/categories.html", "r", encoding="utf-8") as file:
        source = file.read()
    
    soup = BeautifulSoup(markup=source, features="lxml")
    categories = soup.find_all(class_="list-group-item list-group-item-action")
    categories_list = []
    for category in tqdm(categories, desc="Links:"):
        category_dict = {
            "title": "".join([i for i in category.text if not i.isdigit()]).strip(),
            "count": int("".join([i for i in category.text if i.isdigit()]).strip()),
            "link": base_url + category.get("href"),
        }
        categories_list.append(category_dict)

    with open("../extracted_data/afsa_publicreg/categories.json", "w") as file:
        json_object = json.dumps(categories_list, indent=4, ensure_ascii=False)
        file.write(json_object)


def get_categories_pages_html():
    with open("../extracted_data/afsa_publicreg/categories.json", "r", encoding ="utf-8") as file:
        categories = json.load(file)
    
    for category_count, category_value in enumerate(tqdm(categories, position=0, desc="Categories:")):
        category_title = categories[category_count]["title"] # category_title = category_value["title"]
        category_link = categories[category_count]["link"] # category_link = category_value["link"]
        
        response = get_response(url=category_link)
        soup = BeautifulSoup(markup=response, features="lxml")
        pagination = soup.find_all("a", class_="page-link")
        if pagination:
            pages = []
            for page in pagination:
                pages.append(page.get("href"))
            last_page = int("".join([i for i in pages[-2] if i.isdigit()]).strip())
        else:
            last_page = 1
        
        Path(f"../extracted_data/afsa_publicreg/{category_title}").mkdir(parents=True, exist_ok=True)
        for page in tqdm(range(1, last_page + 1), position=1, desc="Pages:"):
            response = get_response(url=category_link + f"?page={page}")
            with open(f"../extracted_data/afsa_publicreg/{category_title}/{category_title}_{page}.html", "w", encoding ="utf-8") as file:
                file.write(response)


def get_registered_entities_links_json():
    files = list(Path("../extracted_data/afsa_publicreg/Registered entities/").glob(pattern="*.html"))
    
    partial_data_list = []
    for file in tqdm(files, position=0, desc="Files:"):
        report = file.read_text(encoding="utf-8")
        soup = BeautifulSoup(markup=report, features="lxml")
        table_data = soup.find("div", class_="table-container").find("table").find("tbody").find_all("tr")
        for item in table_data: # tqdm(table_data, desc="Rows:"):
            table_tds = item.find_all("td")
            partial_json_dict = {
                "company_name": table_tds[1].text.strip(),
                "bin": table_tds[2].text.strip(),
                "organisational_legal_form": table_tds[0].text.strip(),
                "registered_address": table_tds[3].text.strip(),
                "registration_date": table_tds[4].text.strip(),
                "registration_status": table_tds[5].text.strip(),
                "details_url": base_url + table_tds[6].find("a").get("href"),
            }
            partial_data_list.append(partial_json_dict)

    with open("../extracted_data/afsa_publicreg/Registered entities/registered_entities.json", "w", encoding="utf-8") as file:
        json_object = json.dumps(partial_data_list, indent=4, ensure_ascii=False)
        file.write(json_object)


def get_descriptions_registered_entities_pages_html():
    with open("../extracted_data/afsa_publicreg/Registered entities/registered_entities.json", "r", encoding="utf-8") as file:
        source_json = json.load(file)
    
    Path("../extracted_data/afsa_publicreg/Registered entities/Descriptions").mkdir(parents=True, exist_ok=True)
    
    for url_count, url_value in enumerate(tqdm(source_json, desc="Descriptions:")):
        details_url = source_json[url_count]["details_url"] # details_url = url_value["details_url"]
        bin = source_json[url_count]["bin"] # bin = url_value["bin"]
        
        response = get_response(url=details_url)
        with open(f"../extracted_data/afsa_publicreg/Registered entities/Descriptions/description_{bin}.html", "w", encoding="utf-8") as file:
            file.write(response)


def extract_simple_tables(description_data: Tag, table_tag: str):
    extracted_list = []
    extracted_data = description_data.find("div", id=table_tag).find("table", class_="table table-boarded")
    if extracted_data is not None:
        extracted_table = extracted_data.find("tbody").find_all("tr")
        if extracted_table:
            for data in extracted_table:
                tds_data = data.find_all("td")
                if table_tag == "tab1":
                    names_pydantic = OrganizationName(
                        name=normalize_tag(tds_data[0]),
                        status=normalize_tag(tds_data[1], "status"),
                        effective_date=normalize_tag(tds_data[2]),
                        expiration_date=normalize_tag(tds_data[3]),
                    )
                    extracted_list.append(names_pydantic)
                if table_tag == "tab2":
                    addresses_pydantic = OrganizationAddress(
                        address=normalize_tag(tds_data[0]),
                        status=normalize_tag(tds_data[1], "status"),
                        effective_date=normalize_tag(tds_data[2]),
                        expiration_date=normalize_tag(tds_data[2]),
                    )
                    extracted_list.append(addresses_pydantic)
                if table_tag == "tab3":
                    activities_pydantic = OrganizationActivity(
                        code=normalize_tag(tds_data[0], "code"),
                        activity=normalize_tag(tds_data[1]),
                    )
                    extracted_list.append(activities_pydantic)
                if table_tag == "tab4":
                    roles_pydantic = OrganizationRole(
                        role=normalize_tag(tds_data[0]),
                        name=normalize_tag(tds_data[1], "user_name"),
                        effective_date=normalize_tag(tds_data[2]),
                        expiration_date=normalize_tag(tds_data[3]),
                    )
                    extracted_list.append(roles_pydantic)
    return extracted_list


def extract_description_capitals(description_data: Tag):
    shares_list = []
    collaterials_list = []
    shareholders_list = []
    capital_data = description_data.find("div", id="tab5").find_all("table", class_="table table-boarded")
    if capital_data:
        capital_shares = capital_data[0].select("tr:nth-child(1) > td, tr:nth-child(3) > td:nth-child(5)")
        if capital_shares:
            shares_pydantic = OrganizationShareClasses(
                class_name=normalize_tag(capital_shares[0]),
                number_shares=normalize_tag(capital_shares[1], "money_broken_ru"),
                currency=normalize_tag(capital_shares[2]),
                price_per_share=normalize_tag(capital_shares[3], "money_broken_ru"),
                total_cost=normalize_tag(capital_shares[4], "money_broken_ru"),
                summary_total=normalize_tag(capital_shares[4], "money_broken_ru"),
            )
            shares_list.append(shares_pydantic)
        
        capital_collaterials = capital_data[1].find("tbody").find_all("tr")
        if capital_collaterials:
            for collaterial in capital_collaterials:
                tds_data = collaterial.find_all("td")
                collaterials_pydantic = OrganizationCollateralInformation(
                    under_collateral=normalize_tag(tds_data[0]),
                    additional_information=normalize_tag(tds_data[1]),
                )
                collaterials_list.append(collaterials_pydantic)
    
        capital_shareholders = capital_data[2].find("tbody").find_all("tr")
        if capital_shareholders:
            for shareholder in capital_shareholders:
                tds_data = shareholder.find_all("td")
                shareholders_pydantic = OrganizationShareholders(
                    name=normalize_tag(tds_data[0], "user_name"),
                    comments=normalize_tag(tds_data[1]),
                    status=normalize_tag(tds_data[2], "status"),
                )
                shareholders_list.append(shareholders_pydantic)
    return shares_list, collaterials_list, shareholders_list


def find_element_by_text(result_set: ResultSet, text: str):
    for item in result_set:
        p_tag = item.select_one("td:nth-child(1)")
        if p_tag and normalize_tag(p_tag) == text:
            return p_tag.find_next("td").text.strip() if p_tag.find_next("td") else None
        # if text == "статус регистрации":
        #     if p_tag and normalize_tag(p_tag, "status") == "статус регистрации":
        #         found_tag = re.search(r"\b(" + "|".join(value.value for value in Status) + r")\b", normalize_tag(p_tag, "status"), flags=re.IGNORECASE).group(0) # if else None
        #         return found_tag
    return None


def extract_description_licenses(description_data: Tag):
    links_list = []
    licenses_list = []
    license_individuals_list = []
    general_data = description_data.find("div", id="home").find("table", class_="table table-boarded")
    if general_data is not None:
        general_table = general_data.select("tbody > tr")
        if general_table:
            bin_element = find_element_by_text(general_table, "БИН")
            organisational_legal_form_element = find_element_by_text(general_table, "Организационно-правовая форма")
            # registration_status_element = find_element_by_text(general_table, "статус регистрации").lower() # need to remake
            registration_date_element = find_element_by_text(general_table, "Дата регистрации")
            business_nature_element = find_element_by_text(general_table, "Бизнес деятельность")
            
            match_registration_status_element = None
            for item in general_table:
                p_tag = item.select_one("td:nth-child(1)")
                if p_tag and p_tag.text.strip() == "статус регистрации":
                    registration_status_tag = p_tag.find_next("td")
                    if registration_status_tag:
                        registration_status_element = normalize("NFKD", registration_status_tag.text.strip().lower())
                        match_registration_status_element = re.search(r"\b(" + "|".join(value.value for value in Status) + r")\b", registration_status_element, flags=re.IGNORECASE).group(0)
            
            for item in general_table:
                a_tag = item.select_one("td:nth-child(2) > a")
                if a_tag is not None:
                    links_list.append(base_url + a_tag["href"])
            
            for link in links_list:
                response = get_response(url=link)
                soup = BeautifulSoup(markup=response, features="lxml")
                license_data = soup.find_all("table", class_="table table-boarded")
                if license_data:
                    try:
                        license_individuals = license_data[1].select("tbody > tr")
                    except IndexError as e: # Exception
                        license_individuals = []
                    if license_individuals:
                        for item in license_individuals:
                            tds_data = item.select("td")
                            license_individuals_pydantic = OrganizationLicenseIndividual(
                                name=normalize_tag(tds_data[0], "user_name"),
                                role=normalize_tag(tds_data[1]),
                                status=normalize_tag(tds_data[2], "status"),
                                effective_date=normalize_tag(tds_data[3]),
                                expiration_date=normalize_tag(tds_data[4]),
                            )
                            license_individuals_list.append(license_individuals_pydantic)
                    
                    activities_services_set = set()
                    description_set = set()
                    try:
                        license_information = license_data[0].select("td") # tbody > tr
                    except IndexError as e: # Exception
                        license_information = []
                    if license_information:
                        # activities_services_set = {normalize_tag(item) for item in license_information[5].stripped_strings if item is not None or item != ""}
                        for item in license_information[5].stripped_strings:
                            if item is not None and item != "":
                                activities_services_set.add(normalize("NFKD", item.strip()).replace("-", ""))
                        
                        # description_set = {normalize_tag(item) for item in license_information[6].stripped_strings if item is not None or item != ""}
                        for item in license_information[6].stripped_strings:
                            if item is not None and item != "":
                                description_set.add(normalize("NFKD", item.strip()).replace("-", ""))
                    
                    license_pydantic = OrganizationLicense(
                        subject_regulation=normalize_tag(license_information[0]),
                        license_number=normalize_tag(license_information[1]),
                        effective_date=normalize_tag(license_information[2]),
                        expiration_date=normalize_tag(license_information[3]),
                        status=normalize_tag(license_information[4], "status"),
                        activities_services=activities_services_set,
                        description=description_set,
                        comments=normalize_tag(license_information[7]),
                        approved_individuals=license_individuals_list,
                    )
                    licenses_list.append(license_pydantic)
                    
                    # не сохраняются - надо исправить
                    # with open(f"./src/extracted_data/afsa_publicreg/Registered entities/Licenses_html/license_{normalize_tag(license_information[1])}", "r", encoding="utf-8") as file:
                    #     file.write(response)
                    
    return bin_element, business_nature_element, organisational_legal_form_element, registration_date_element, match_registration_status_element, licenses_list


def parse_description_pages_registered_entities():
    Path("./src/extracted_data/afsa_publicreg/Registered entities/Licenses_html/").mkdir(parents=True, exist_ok=True)
    Path("./src/extracted_data/afsa_publicreg/Registered entities/Descriptions_json_enumless/").mkdir(parents=True, exist_ok=True)
    files = list(Path("./src/extracted_data/afsa_publicreg/Registered entities/Descriptions_html/").glob(pattern="*.html"))
    for file in tqdm(files, desc="Files:"):
        description = file.read_text(encoding="utf-8")
    
        # with open("./src/extracted_data/afsa_publicreg/Registered entities/Descriptions_html/description_171140900016_ru.html", "r", encoding="utf-8") as file:
        #     description = file.read()
            
        soup = BeautifulSoup(markup=description, features="lxml")
        description_data = soup.find("div", class_="tab-content")

        # organizations_list = []
        organization_pydantic = Organization(
            bin=extract_description_licenses(description_data)[0],
            business_nature=extract_description_licenses(description_data)[1],
            organisational_legal_form=extract_description_licenses(description_data)[2],
            registration_date=extract_description_licenses(description_data)[3],
            registration_status=extract_description_licenses(description_data)[4],
            licenses=extract_description_licenses(description_data)[5],
            names=extract_simple_tables(description_data, "tab1"),
            addresses=extract_simple_tables(description_data, "tab2"),
            activities=extract_simple_tables(description_data, "tab3"),
            roles=extract_simple_tables(description_data, "tab4"),
            share_classes=extract_description_capitals(description_data)[0],
            collateral_information=extract_description_capitals(description_data)[1],
            shareholders=extract_description_capitals(description_data)[2],
        )
        # organizations_list.append(organization_pydantic)

        with open(f"./src/extracted_data/afsa_publicreg/Registered entities/Descriptions_json_enumless/description_{extract_description_licenses(description_data)[0]}.json", "w", encoding="utf-8") as file:
            file.write(organization_pydantic.model_dump_json(indent=4))
        
    # with open(f"../extracted_data/afsa_publicreg/Registered entities/Testing Pydantic/testing_pydantic_model_{texts_list_new[0]}.json", "w", encoding="utf-8") as file:
    #     result = [item.model_dump_json(indent=4) for item in organizations_list] # model_dump()
    #     file.write(result)

parse_description_pages_registered_entities()
