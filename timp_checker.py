# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 21:44:52 2021

@author: Xabi
"""

from selenium import webdriver
from datetime import datetime
import pandas as pd

def url_builder(place):
    centro = '8154-bidasoa-21-gestion-deportiva-2017-slu-polideportivos-municipales-artaleku-azken-portu'
    map_centros = {'azken_gym':'53181',
                   'azken_pool':'55107',
                   'artaleku_pool':'55105',
                   'artaleku_gym':'53179'}
    if place in map_centros.keys():
        url = f'https://connect.timp.pro/{centro}/activities/{map_centros[place]}'
        return url
    else:
        raise Exception(f"No activity names {place}")

def get_place_status(driver, place, debug=False):
    url = url_builder(place)
    driver.get(url)
    
    # Create slot container
    df = pd.DataFrame(columns=['start_time', 'end_time', 'status', 'id'])
    
    # List all dates
    span = driver.find_elements_by_class_name("date-card")
    date_urls = []
    for e in span:
        date_url = e.get_attribute("href")
        #date = datetime.strptime(date_url.split("date=")[-1], "%Y-%m-%d")
        date = date_url.split("date=")[-1]
        if debug:
            print(date)
        date_urls.append(date_url)
    
    for date_url in date_urls:
        # List all slots
        driver.get(date_url)
        date = datetime.strptime(date_url.split("date=")[-1], "%Y-%m-%d")
        slots = driver.find_elements_by_class_name("text-reset")
        for s in slots:
            status = s.find_element_by_class_name("mb-0")
            times = s.find_element_by_class_name("p-3")
            if debug:
                print(status.text, times.text)
            start_h = datetime.strptime(times.text.split("\n")[0], "%H:%M")
            start_h = datetime(date.year, date.month, date.day,
                               start_h.hour, start_h.minute)
            end_h = datetime.strptime(times.text.split("\n")[1], "%H:%M")
            end_h = datetime(date.year, date.month, date.day,
                               end_h.hour, end_h.minute)
            if status.text == 'Disponible':
                status = 'available'
            else:
                status = 'busy'
            href_id = s.get_attribute("href").split("/")[-1]
            slot_dict = {'start_time': start_h, 'end_time': end_h, 'status': status,
                         'id':href_id, 'place': place}
            df = df.append(slot_dict, ignore_index=True)
    return df

if __name__ == '__main__':
    driver = webdriver.Firefox()
    
    df = get_place_status(driver, 'azken_pool')

    driver.close()
     