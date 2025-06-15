import re
from datetime import datetime
import os
import json

class RegexExtractor:
    def __init__(self):
        self.patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'(?:(?:\+?\d{1,3})?[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?){2,3}\d{3,4}',
            'linkedin': r'(?:linkedin\.com/in/|linkedin\.com/pub/)([a-zA-Z0-9-]+)',
            'date': r'\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{4}\b|\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b|\b\d{4}\b',
            'education_degree': r'\b(?:Bachelor|Master|PhD|Ph\.D|MBA|B\.S\.|M\.S\.|B\.A\.|M\.A\.|BSc|MSc|BA|MA|BBA|A\.A\.|Associates?|Diploma|Certificate|High School Diploma)\b',
            'years_experience': r'\b\d+\+?\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|exp)?\b',
        }
        self.debug_mode = True # This can be set to False to disable saving debug files
        self.current_filename = ""

    def save_debug(self, step, content):
        """Save debug information if debug_mode is True."""
        if self.debug_mode:
            debug_dir = "debug_regex_extraction"
            os.makedirs(debug_dir, exist_ok=True)
            
            filename_base = self.current_filename if self.current_filename else "unknown_cv"
            filename = f"{filename_base}_{step}.txt"
            filepath = os.path.join(debug_dir, filename)
            
            try:
                with open(filepath, 'w', encoding='utf-8', errors='ignore') as f:
                    f.write(content)
            except Exception as e:
                print(f"Error saving debug file {filepath}: {e}")

    def extract_personal_info(self, text):
        """Extract personal information from CV text"""
        info = {}
        try:
            text_start = text[:1000]
            
            email_match = re.search(self.patterns['email'], text)
            if email_match:
                info['email'] = email_match.group(0)
            
            phone_patterns = [
                r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b',
                r'\+1\s*\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b',
                r'\(\d{3}\)\s*\d{3}[-.\s]?\d{4}\b'
            ]
            for pattern in phone_patterns:
                phone_match = re.search(pattern, text_start)
                if phone_match:
                    info['phone'] = phone_match.group(0).strip()
                    break
            
            lines = text.split('\n')
            for i, line in enumerate(lines[:5]):
                line = line.strip()
                if not line: continue
                if any(header in line.upper() for header in ['SUMMARY', 'OBJECTIVE', 'SKILLS', 'EXPERIENCE', 'EDUCATION', 'PROFILE']):
                    continue
                if len(line) < 50:
                    if line.isupper() and ' ' in line and len(line.split()) > 1 and len(line.split()) < 4 :
                        is_likely_name = True
                        for word in line.split():
                            if word in ['ACCOUNTANT', 'MANAGER', 'ENGINEER', 'DEVELOPER', 'ANALYST', 'ADVOCATE', 'SUMMARY', 'OBJECTIVE', 'SKILLS', 'EXPERIENCE', 'PROFILE']:
                                is_likely_name = False
                                break
                        if is_likely_name:
                            info['name'] = line.title()
                            break
                    elif re.match(r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2}$', line):
                        info['name'] = line
                        break
            # self.save_debug("1_personal_info", f"Personal Info Extracted:\n{json.dumps(info, indent=2)}")
        except Exception as e:
            # self.save_debug("1_personal_info_error", f"Error in extract_personal_info: {str(e)}")
            print(f"Error in extract_personal_info: {str(e)}")
        return info

    def extract_summary(self, text):
        """Extract summary/objective section"""
        summary = ""
        try:
            summary_patterns = [
                r'Summary\s*\n+(.*?)(?=\n(?:Skills|Experience|Education|Highlights|Accomplishments|Core Competencies)|$)',
                r'Objective\s*\n+(.*?)(?=\n(?:Skills|Experience|Education|Highlights|Accomplishments|Core Competencies)|$)',
                r'Profile\s*\n+(.*?)(?=\n(?:Skills|Experience|Education|Highlights|Accomplishments|Core Competencies)|$)'
            ]
            
            for pattern in summary_patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
                if match:
                    summary_text = match.group(1).strip()
                    summary_text = re.sub(r'\s+', ' ', summary_text)
                    if 20 < len(summary_text) < 1000:
                        # self.save_debug("2_summary", f"Pattern: {pattern}\n\nExtracted Summary:\n{summary_text}")
                        summary = summary_text[:500]
                        return summary
            # self.save_debug("2_summary", "No summary found or summary too short/long.")
        except Exception as e:
            # self.save_debug("2_summary_error", f"Error in extract_summary: {str(e)}")
            print(f"Error in extract_summary: {str(e)}")
        return summary

    def extract_skills(self, text):
        """Extract skills section"""
        skills = []
        try:
            skills_section_patterns = [
                r'Skills\s*\n+(.*?)(?=\n(?:Experience|Education|Employment|Professional Affiliations|Interests|Awards)|$)',
                r'Technical Skills\s*\n+(.*?)(?=\n(?:Experience|Education|Employment|Professional Affiliations)|$)',
                r'Core Competencies\s*\n+(.*?)(?=\n(?:Experience|Education|Employment|Professional Affiliations)|$)',
                r'Highlights\s*\n+(.*?)(?=\n(?:Experience|Education|Employment|Accomplishments)|$)'
            ]
            
            skills_text_content = ""
            for pattern in skills_section_patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
                if match:
                    skills_text_content = match.group(1).strip()
                    # self.save_debug("3a_skills_section", f"Pattern: {pattern}\n\nExtracted Section:\n{skills_text_content}")
                    break
            
            temp_skills_list = []
            if skills_text_content:
                lines = skills_text_content.split('\n')
                for line in lines:
                    line = line.strip()
                    if not line: continue
                    
                    line = re.sub(r'^[•\-*]\s*', '', line)
                    
                    if ':' in line:
                        parts = line.split(':', 1)
                        if len(parts) == 2:
                            skill_list_after_colon = parts[1]
                            sub_skills_from_colon = re.split(r'[,;]', skill_list_after_colon)
                            for skill_item in sub_skills_from_colon:
                                skill_item = skill_item.strip().rstrip('.')
                                if 2 < len(skill_item) < 50 and skill_item:
                                    temp_skills_list.append(skill_item)
                    else:
                        if ';' in line or (',' in line and line.count(',') > 0 and line.count(',') < 5) :
                            sub_skills_from_line = re.split(r'[,;]', line)
                            for skill_item in sub_skills_from_line:
                                skill_item = skill_item.strip().rstrip('.')
                                if 2 < len(skill_item) < 50 and skill_item:
                                    temp_skills_list.append(skill_item)
                        elif 2 < len(line) < 100 and not any(header in line.upper() for header in ['EXPERIENCE', 'EDUCATION', 'CERTIFICATIONS']):
                            temp_skills_list.append(line.rstrip('.'))

            tech_skills_found = set()
            tech_pattern = r'\b(?:Python|Java|JavaScript|TypeScript|C\+\+|C#|PHP|Ruby|Swift|Kotlin|Go|R\b|SQL|NoSQL|MongoDB|MySQL|PostgreSQL|Oracle|HTML5?|CSS3?|React|Angular|Vue|Node\.js|Django|Flask|Spring|\.NET|Docker|Kubernetes|AWS|Azure|GCP|Git|Machine Learning|Data Analysis|Data Science|AI|DevOps|Linux|Windows|Excel|Word|PowerPoint|Outlook|QuickBooks|Accounting|General Accounting|Accounts Payable|Payroll|Financial Analysis|Financial Reporting|Budget(?:ing)?|Audit(?:ing)?|Tax(?:ation)?|GAAP|SAP|ERP|Program Management|Project Management|Customer Service|Communication|Leadership|Teamwork|Problem Solving|Microsoft Office|CPA)\b'
            tech_matches = re.findall(tech_pattern, text, re.IGNORECASE)
            for tech in tech_matches:
                tech_skills_found.add(tech)
            
            temp_skills_list.extend(list(tech_skills_found))
            
            seen = set()
            unique_skills = []
            for skill_val in temp_skills_list:
                skill_lower = skill_val.lower().strip()
                if skill_lower not in seen and skill_lower:
                    seen.add(skill_lower)
                    unique_skills.append(skill_val)
            
            skills = unique_skills
            # self.save_debug("3b_skills_final", f"Total skills found: {len(skills)}\n\n" + "\n".join(f"- {s}" for s in skills))
        except Exception as e:
            # self.save_debug("3_skills_error", f"Error in extract_skills: {str(e)}")
            print(f"Error in extract_skills: {str(e)}")
        return skills[:20]

    def extract_experience(self, text):
        """Extract work experience"""
        experience = []
        exp_text = ""
        try:
            exp_section_pattern = r'\w*(?:Professional Experience|Experience|Work History)\s*\n+(.*?)(?=\n(?:Education|Skills|Certifications|Interests|Additional Information|Professional Affiliations|Languages)|$)*'
            exp_match = re.search(exp_section_pattern, text, re.IGNORECASE | re.DOTALL)
            
            if exp_match:
                exp_text = exp_match.group(1).strip()
                # self.save_debug("4a_experience_section", f"Experience Section Found:\n{exp_text}")
            else:
                # self.save_debug("4a_experience_section", "No Experience Section Found with primary pattern.")
                return []

            pattern_original_mm_yyyy = r'(\d{1,2}/\d{4})\s+to\s+(\d{1,2}/\d{4}|Current|Present)\s*\n+([^\n]+?)\s+Company\s*Name\s*:\s*([^\n]+)'
            pattern_original_pos_company_loc = r'([A-Za-z\s,/\-]+?)\s+Company\s*Name\s*:\s*([^\n]+)'
            pattern_accountant_job = r'^(Company Name)\s*\n+([A-Za-z]+\s+\d{4})\s+to\s+([A-Za-z]+\s+\d{4}|Current|Present)\s*\n+([^\n]+?)\s*\n+([^\n]*(?:City|State)[^\n]*)\s*\n+'

            job_patterns = [
                pattern_original_mm_yyyy,
                pattern_accountant_job,
                pattern_original_pos_company_loc,
            ]

            all_exp_matches = []
            matched_pattern_type = None
            
            for idx, pattern_str in enumerate(job_patterns):
                flags = re.IGNORECASE | re.DOTALL
                if pattern_str.startswith('^'):
                    flags |= re.MULTILINE
                current_matches = list(re.finditer(pattern_str, exp_text, flags))
                if current_matches:
                    # self.save_debug(f"4b_job_matches_pattern_{idx}", f"Found {len(current_matches)} jobs with pattern index {idx}:\n{pattern_str}")
                    all_exp_matches = current_matches
                    if pattern_str == pattern_original_mm_yyyy: matched_pattern_type = "original_mm_yyyy"
                    elif pattern_str == pattern_accountant_job: matched_pattern_type = "accountant_month_yyyy"
                    elif pattern_str == pattern_original_pos_company_loc: matched_pattern_type = "original_pos_company_loc"
                    break 
            
            if all_exp_matches:
                # self.save_debug("4b_job_matches_summary", f"Processing {len(all_exp_matches)} jobs with pattern type: {matched_pattern_type}")
                for i, match_obj in enumerate(all_exp_matches):
                    exp_entry = ""
                    company = ""
                    position = ""
                    start_date = ""
                    end_date = ""
                    location = ""

                    if matched_pattern_type == "original_mm_yyyy":
                        start_date = match_obj.group(1)
                        end_date = match_obj.group(2)
                        position = match_obj.group(3).strip()
                        company_or_location = match_obj.group(4).strip() if match_obj.lastindex >= 4 else ""
                        company = company_or_location 
                        exp_entry = f"{position} at {company}\n{start_date} - {end_date}"
                    
                    elif matched_pattern_type == "accountant_month_yyyy":
                        company_placeholder = match_obj.group(1).strip()
                        start_date = match_obj.group(2).strip()
                        end_date = match_obj.group(3).strip()
                        position = match_obj.group(4).strip()
                        location = match_obj.group(5).strip()
                        company = location if company_placeholder.lower() == "company name" else company_placeholder
                        exp_entry = f"{position} at {company}\n{start_date} - {end_date}"

                    elif matched_pattern_type == "original_pos_company_loc":
                        position = match_obj.group(1).strip()
                        company = match_obj.group(2).strip() 
                        before_text = exp_text[:match_obj.start()]
                        date_pattern_exp = r'([A-Za-z]+\s+\d{4}|\d{1,2}/\d{4})\s+to\s+([A-Za-z]+\s+\d{4}|\d{1,2}/\d{4}|Current|Present)'
                        date_match_exp = None
                        for dm_exp in reversed(list(re.finditer(date_pattern_exp, before_text))):
                            date_match_exp = dm_exp
                            break
                        if date_match_exp:
                            start_date = date_match_exp.group(1)
                            end_date = date_match_exp.group(2)
                            exp_entry = f"{position} at {company}\n{start_date} - {end_date}"
                        else:
                            exp_entry = f"{position} at {company}"
                    
                    if exp_entry:
                        start_pos_resp = match_obj.end()
                        end_pos_resp = len(exp_text)
                        if i + 1 < len(all_exp_matches):
                            end_pos_resp = all_exp_matches[i+1].start()
                        
                        resp_text_segment = exp_text[start_pos_resp:end_pos_resp].strip()
                        responsibilities_list = []
                        resp_lines = resp_text_segment.split('\n')
                        for resp_line in resp_lines:
                            resp_line = resp_line.strip()
                            resp_line = re.sub(r'^[•*-]\s*', '', resp_line)
                            if resp_line and len(resp_line) > 10 and \
                               not re.match(r'([A-Za-z]+\s+\d{4}|\d{1,2}/\d{4})\s+to', resp_line) and \
                               not resp_line.lower().startswith("company name"):
                                responsibilities_list.append(f"• {resp_line}")
                                if len(responsibilities_list) >= 2:
                                    break
                        if responsibilities_list:
                            exp_entry += "\n" + "\n".join(responsibilities_list)
                        experience.append(exp_entry)
                    if len(experience) >= 5: break
            # else:
                 # self.save_debug("4b_job_matches_summary", "No job matches found with any defined patterns.")
            # self.save_debug("4c_experience_final", f"Total experience entries: {len(experience)}\n\n" + "\n\n---\n\n".join(experience))
        except Exception as e:
            # self.save_debug("4_experience_error", f"Error in extract_experience: {str(e)}\n\nStack trace:\n{e.__traceback__}")
            print(f"Error in extract_experience: {str(e)}")
        return experience[:5]

    def extract_education(self, text):
        """Extract education information"""
        education = []
        edu_text = ""
        try:
            edu_patterns_main = [
                r'Education(?:\s+and\s+Training)?\s*\n+(.*?)(?=\n(?:Skills|Professional Affiliations|Certifications|Interests|Additional Information|Awards|Languages)|$)',
                r'Education\s*\n+(.*?)$' 
            ]
            
            for pattern in edu_patterns_main:
                match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
                if match:
                    edu_text = match.group(1).strip()
                    # self.save_debug("5a_education_section", f"Pattern: {pattern}\n\nEducation Section:\n{edu_text}")
                    break
            
            if edu_text:
                pattern_edu_aa_field_year = r'([A-Z]\.[A-Z]\.|Bachelor|Master|MBA|BBA|PhD|Diploma|Certificate)\s*:\s*([^,\n]+?)(?:\s*,\s*(\d{4}))?'
                pattern_edu_month_year_degree_fieldinst = r'([A-Za-z]+\s+\d{4})\s+([^:]+)\s*:\s*([^\n]+)'
                pattern_edu_degree_of_field_inst = r'(Bachelor|Master|MBA|BBA|PhD)\s+(?:of\s+)?([^,\n]+?)(?:\s+(?:from|at)\s+)?([A-Z][^\n]*(?:University|College|Institute|School))'
                pattern_edu_consumer_advocate = r'^(Certificate[^\n]*\.\s*)\n+([A-Z][A-Za-z\s.,&-]+(?:Association|Institute|School|College|University))\s*(?:\n*:\s*\n*([A-Za-z\s]+,\s*[A-Z]{2}))?'
                pattern_edu_accountant = r'^([A-Z][A-Za-z\s.,-]+(?:University|College|Institute|School))\s*\n+(\d{4})\s*\n+([A-Za-z.\s()]+?)\s*:\s*([^,\n]+)'

                degree_patterns_list = [
                    pattern_edu_aa_field_year,
                    pattern_edu_month_year_degree_fieldinst,
                    pattern_edu_degree_of_field_inst,
                    pattern_edu_consumer_advocate,
                    pattern_edu_accountant
                ]
                
                for pattern_str in degree_patterns_list:
                    flags = re.IGNORECASE | re.DOTALL
                    if pattern_str.startswith('^'):
                        flags |= re.MULTILINE
                    
                    matches = list(re.finditer(pattern_str, edu_text, flags))
                    
                    if matches:
                        # self.save_debug("5b_degree_matches", f"Pattern: {pattern_str}\nFound {len(matches)} matches for education")
                        for match_obj in matches:
                            groups = match_obj.groups()
                            edu_entry = ""
                            year = "" # Initialize year to check if it's found by specific patterns

                            if pattern_str == pattern_edu_aa_field_year:
                                degree = groups[0]
                                field = groups[1].strip()
                                year = groups[2] if len(groups) > 2 and groups[2] else ""
                                after_text = edu_text[match_obj.end():match_obj.end()+200]
                                inst_match_edu = re.search(r'([A-Z][^\n:,]+(?:University|College|Institute|School))', after_text)
                                institution = inst_match_edu.group(1).strip() if inst_match_edu else ""
                                if institution: edu_entry = f"{degree} in {field} - {institution}"
                                else: edu_entry = f"{degree} in {field}"
                                if year: edu_entry += f" ({year})"

                            elif pattern_str == pattern_edu_month_year_degree_fieldinst:
                                date = groups[0] # This contains year
                                year = re.search(r'\d{4}', date).group(0) if re.search(r'\d{4}', date) else ""
                                degree_text = groups[1].strip()
                                field_and_inst = groups[2].strip()
                                inst_match_edu = re.search(r'([A-Z][^\n]+(?:University|College|Institute|School))', field_and_inst)
                                if inst_match_edu:
                                    institution = inst_match_edu.group(1).strip()
                                    field = field_and_inst.replace(institution, '').strip()
                                    edu_entry = f"{degree_text} in {field} - {institution} ({date})"
                                else:
                                    edu_entry = f"{degree_text} in {field_and_inst} ({date})"
                            
                            elif pattern_str == pattern_edu_degree_of_field_inst:
                                degree = groups[0].strip()
                                field = groups[1].strip()
                                institution = groups[2].strip() if len(groups) > 2 and groups[2] else ""
                                edu_entry = f"{degree} in {field}"
                                if institution: edu_entry += f" - {institution}"
                                context_around_match = edu_text[max(0, match_obj.start()-50) : min(len(edu_text), match_obj.end()+50)]
                                year_match_edu = re.search(r'\b((?:19|20)\d{2})\b', context_around_match)
                                if year_match_edu and not year in edu_entry :
                                    edu_entry += f" ({year_match_edu.group(1)})"
                                    year = year_match_edu.group(1) # Store found year
                            
                            elif pattern_str == pattern_edu_consumer_advocate:
                                description = groups[0].strip()
                                institution = groups[1].strip()
                                location = groups[2].strip() if len(groups) > 2 and groups[2] else ""
                                edu_entry = f"{description} - {institution}"
                                if location: edu_entry += f" ({location})"
                            
                            elif pattern_str == pattern_edu_accountant:
                                institution = groups[0].strip()
                                year = groups[1].strip()
                                degree = groups[2].strip()
                                field = groups[3].strip()
                                edu_entry = f"{degree} in {field} - {institution} ({year})"

                            if edu_entry and edu_entry not in education:
                                education.append(edu_entry)
                            if len(education) >= 3: break
                        if education: break
                
                if not education:
                    # self.save_debug("5b_degree_matches", "No matches with primary patterns, trying fallback.")
                    degree_keyword_matches = list(re.finditer(self.patterns['education_degree'], edu_text, re.IGNORECASE))
                    for dk_match in degree_keyword_matches:
                        start_context = max(0, dk_match.start() - 70)
                        end_context = min(len(edu_text), dk_match.end() + 100)
                        context = edu_text[start_context:end_context].strip()
                        context = re.sub(r'\s+', ' ', context)
                        context_lines = context.split('\n')
                        best_context_line = ""
                        for c_line in context_lines:
                            if dk_match.group(0) in c_line:
                                best_context_line = c_line.strip()
                                break
                        if not best_context_line: best_context_line = context
                        if best_context_line and best_context_line not in education:
                            education.append(best_context_line)
                            if len(education) >= 3: break
            # self.save_debug("5c_education_final", f"Total education entries: {len(education)}\n\n" + "\n".join(f"- {e}" for e in education))
        except Exception as e:
            # self.save_debug("5_education_error", f"Error in extract_education: {str(e)}")
            print(f"Error in extract_education: {str(e)}")
        return education[:3]

    def extract_all(self, text):
        """Extract all information from CV text"""
        try:
            if hasattr(self, '_current_cv_path_for_debug'):
                self.current_filename = os.path.basename(self._current_cv_path_for_debug).replace('.pdf', '')
            elif 'unknown' not in self.current_filename and self.current_filename :
                 pass
            else:
                first_line = text.split('\n')[0].strip()
                potential_name = "".join(c for c in first_line if c.isalnum() or c == ' ')[:30].replace(" ","_")
                self.current_filename = potential_name if potential_name else "unknown_cv"

            # self.save_debug("0_original_text", f"Text length: {len(text)}\nLine count: {len(text.split(chr(10)))}\n\n{text}")
            
            if len(text) > 70000:
                text = text[:70000]
                # self.save_debug("0_text_truncated", "Text was truncated to 70000 characters")
            
            result = {
                'personal_info': self.extract_personal_info(text),
                'summary': self.extract_summary(text),
                'skills': self.extract_skills(text),
                'experience': self.extract_experience(text),
                'education': self.extract_education(text)
            }
            
            # self.save_debug("6_final_result", json.dumps(result, indent=2))
            return result
            
        except Exception as e:
            error_msg = f"Error in extract_all: {str(e)}"
            # self.save_debug("error_extract_all", error_msg)
            print(f"Error in extract_all: {str(e)}") # Also print to console
            return {
                'personal_info': {}, 'summary': '', 'skills': [],
                'experience': [], 'education': []
            }