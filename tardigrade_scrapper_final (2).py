from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import bs4
import time
import csv
import os

def get_soup(url):
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    return soup

def table_writer(url,table,pos):

    f = open("tardigrade_tables.csv", 'a')
    writer = csv.writer(f)

    q_id = re.split("-",url)[-1]
    rows = table.find_all('tr')

    for i in rows:
        row_list = [q_id,pos]
        if i == rows[0]:
            columns = i.find_all('th')
        else:
            columns = i.find_all('td')
        for j in columns:
            row_list.append(j.text)
        writer.writerow(row_list)

    f.close()

def table_soup(url,soup):
    soup_row = [url,soup]
    f = open("url_soup.csv", 'a')
    writer = csv.writer(f)
    writer.writerow(soup_row)
    f.close()
    

def get_question_details(url,soup):
    temp_data = {}
    temp_df = pd.DataFrame()
    q_id = ques = raw_ques = cor_ans = soln = raw_soln = img_in_ques = img_in_sol = ques_img_links = \
    sol_img_links = table_in_ques = table_in_soln = table_html =''
    crumbs = all_tags = all_options = {}
    
    #Question ID
    try:
        q_id = re.split("-",url)[-1]
    except:
        q_id = "N/A"
    
    #Breadcrumbs
    try:
        breadcrumbs = soup.find('ol',class_ = 'bc').find_all('li')
        crumbs = {}
        for i,j in zip(breadcrumbs,range(len(breadcrumbs))):
            crumbs['crumb_'+str(j+1)] = i.text
    except:
        crumbs = {}
    
    #Question
    try:
        q = soup.find('div', class_ = 'qc-h')
        question = q.find('h1')
        
        table = q.find('table')
        if table is None:
            table_in_ques = 'No'
        else:
            table_writer(url,table,'question')
            table_in_ques = 'Yes'
            table_html = table
        
        for i in question.contents:
            if isinstance(i, bs4.element.NavigableString):
                ques+=i.string
            elif isinstance(i,bs4.element.Tag):
                if 'image' in i.attrs.values():
                    img_in_ques = "Yes"
                    image = i.attrs['src']
                    ques= ques+"\n"+ image+"\n"
                    ques_img_links = ques_img_links+image+", "
        
        #Raw Question
        raw_ques = question.text
    except:
        ques = "N/A"
        raw_ques = "N/A"
    
    #Tags
    try:
        tags = q.find('div', class_ = 'qp-tg').find_all('span')
        all_tags = {}
        for i,j in zip(tags[:-1], range(len(tags[:-1]))):
            all_tags['tag_'+str(j+1)]= i.text
    except:
        all_tags = {}
        
    #Options
    try: 
        options = soup.find_all('div', class_ = 'qc-o')
        all_options = {}
        for i,j in zip(options[:-1], range(len(options[:-1]))):
            lab = i.find('label')
            for k in lab.children:
                if k.name == 'h2':
                    all_options['opt_'+str(j+1)]= k.string
                    if 'correct' in i.attrs['class']:
                        cor_ans = i.find('h2').text
                elif k.name == 'img':
                    all_options['opt_'+str(j+1)]= k.attrs['src']
                    if 'correct' in i.attrs['class']:
                        cor_ans = k.attrs['src']
    except:
        all_options = {}
        cor_ans = "N/A"
    
    #Solution
    try:
        solution_block = soup.find('div', class_ = 'qc-sol')
        solution = solution_block.find('h2')
        
        table = solution_block.find('table')
        if table is None:
            table_in_soln = 'No'
        else:
            table_writer(url,table,'solution')
            table_in_soln = 'Yes'
            table_html = table
        
        for i in solution.contents:
            if isinstance(i, bs4.element.NavigableString):
                soln+=i.string
            elif isinstance(i,bs4.element.Tag):
                if 'image' in i.attrs.values():
                    img_in_sol = "Yes"
                    image = i.attrs['src']
                    soln = soln+"\n"+ image+"\n"
                    sol_img_links = sol_img_links+image+", "
        #Raw Solution
        raw_soln = solution.text
    except:
        soln = "N/A"
        raw_soln = "N/A"
    j=0
    ans=0
    for i in all_options.values():
        j=j+1
        if cor_ans == i :
            ans = j
    
    
    temp_data = {'url':url,'question_id':q_id,'question':ques,'correct_answer':cor_ans,'solution':soln, \
                 'Raw_Question_Format' : raw_ques, 'Raw_solution' : raw_soln, 'Image_in_Question': img_in_ques,\
                 'Image_in_solution' : img_in_sol, 'Question_image_links' : ques_img_links,\
                 'Table_in_question':table_in_ques,'Table_in_solution':table_in_soln,\
                 'Table_html': table_html,'Solution_image_links':sol_img_links,'ans':ans}
    temp_data.update(all_options)
    temp_data.update(all_tags)
    temp_data.update(crumbs)
    
    temp_df = temp_df.append(temp_data, ignore_index = True)
    
    return temp_df




final_df = pd.DataFrame()
urls = pd.read_csv("Tardi_urls.csv")
k=0

for i in urls['url'][:10]:
    time.sleep(4)
    print(i)
    try:
        soup = get_soup(i)
        # table_soup(i,soup)
        k=k+1
        print(k)
    except:
        k = 2
        print(k)
        continue
    df = get_question_details(i,soup)
    final_df = final_df.append(df, ignore_index = True)
    

final_df.to_csv("tardi.csv")