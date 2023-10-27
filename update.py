import re
import fileinput

def extract_company(s: str, pttn):
    s = s.strip('*')
    m = re.match(pttn, s)
    if m is not None:
        s = m.group(1)
    return s

def extract_role_info(s: str):
    pattern = re.compile(r'^\|.+?\|.+?\|.+?\|.+?\|.+?\|$')
    comp = re.compile(r'\[(.+)\]\(http.+\)')
    m = re.match(pattern, s)
    if m is None:
        return
    content = m.group(0).strip().strip('|').split('|')
    content = [s.strip() for s in content]
    company = extract_company(content[0], comp)
    role = content[1]
    location = content[2]
    return company, role, location


def collect_records(file):
    records = set()
    with open(file, 'r', encoding='utf-8') as f:
        prev_company = None
        for line in f:
            res = extract_role_info(line)
            if res is None:
                continue
            company, role, location = res
            if company.strip() == '↳':
                company = prev_company
            prev_company = company
            if role.startswith('✔'):
                role = role[2:]
                records.add((company, role, location))
    return records

def dump_records(records: list, save_path='records.txt'):
    with open(save_path, 'w', encoding='utf-8') as f:
        for record in sorted(records):
            f.write('\t'.join(record))
            f.write('\n')

def load_records(file: str = 'records.txt'):
    records = set()
    with open(file, 'r', encoding='utf-8') as f:
        for line in f:
            res = line.strip().split('\t')
            records.add(tuple(res))
    return records

def update(file: str, records: set):
    with fileinput.FileInput(file, inplace=True, backup='.bak', encoding='utf-8') as f:
        # updated on Sep 26 as the format changed
        prev_company = None
        for line in f:
            # Modify the line as needed
            res = extract_role_info(line)
            if res is not None:
                company, role, location = res
                if company.strip() == '↳':
                    company = prev_company
                    res = (company, role, location)
                prev_company = company
                if res in records:
                    if f'✔ {role}' not in line:
                        line = line.replace(role, f'✔ {role}')
            print(line, end='')


if __name__ == '__main__':
    records = collect_records('README.md')
    dump_records(records)
    # records = load_records()
    # update('README.md', records)