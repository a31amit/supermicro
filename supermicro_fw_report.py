#!/usr/bin/env python
import sys
import requests
import lxml.html as lhtml
import json
import argparse


def get_firmware_details(cpu_vendor, mbd_model):

    vendor_number = {
        'INTEL': '1',
        'AMD': '2'
    }

    vendorId = vendor_number.get(cpu_vendor.upper(), None)

    if vendorId is None:
        return None

    supermicro_base_url = 'https://www.supermicro.com'
    download_url = supermicro_base_url + \
        '/support/resources/getfile.php?SoftwareItemID='
    search_url = supermicro_base_url + \
        '/support/resources/bios_ipmi.php?vendor=1&keywords=X10SDV-4C-7TP4F'
    # search_url = supermicro_base_url + '/support/resources/bios_ipmi.php?vendor=1&keywords=' + %s

    search_url = supermicro_base_url + \
        "/support/resources/bios_ipmi.php?vendor=%s&keywords=%s" % (
            vendorId, mbd_model)

    page = requests.get(search_url)
    tree = lhtml.fromstring(page.content)
    tables = tree.xpath('//table[@class="biosipmiTable"]')
    data_table = []
    table_headers = ['Model', 'Rev', 'Download ZIP',
                     'Release Notes', 'Part#', 'Description', 'Name']

    for table in tables:
        for element_num in range(1, len(table)):
            temp_dict = {}
            temp_dict['model_url'] = 'Not Found'
            temp_dict['download_zip_url'] = 'Not Found'
            for header_num in range(0, len(table_headers)):
                temp_dict[table_headers[header_num]
                          ] = table[element_num][header_num].text_content()
                if table_headers[header_num] == 'Model':
                    temp_dict['model_url'] = supermicro_base_url + \
                        table[element_num][header_num][0].get('href', '')
                if table_headers[header_num] == 'Download ZIP':
                    package_href = str(table[element_num]
                                       [header_num][0].get('href', ''))
                    packageId = package_href.split('=')[1].strip()
                    temp_dict['download_zip_url'] = download_url + packageId

            data_table.append(temp_dict)

    return data_table





if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='=> Supermicro Mother Board & IPMI Firmware Details')
    parser.add_argument('--cpu', action='store', choices=[
                        'INTEL', 'AMD'], default='INTEL', help='CPU Manufracture NAME', required=True, dest='cpu')
    parser.add_argument('--motherboard', action='store',
                        help='MotherBoard Model', dest='mbdname', required=True)
    user_input = parser.parse_args()

    try:
        d_table = get_firmware_details(cpu_vendor=user_input.cpu,
                             mbd_model=user_input.mbdname)
    except:
        print "Something Wrong"

    if d_table is None:
        print("Didn't receive data")
        sys.exit(1)

    if len(d_table) is 0:
        print("Nothing Found")
    else:
        for items in d_table:
            print(json.dumps(items, sort_keys=True, indent=4))
            print ("")
        
