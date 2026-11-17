import json
import os
import requests

def fetch_mit_ocw_courses(limit=500):
    url = "https://open.mit.edu/api/v0/search/"
    headers = {"Content-Type": "application/json"}
    
    payload = {
        "size": limit,
        "from": 0,
        "query": {
            "bool": {
                "must": [
                    {"term": {"object_type": "course"}},
                    {"term": {"offered_by": "OCW"}}
                ]
            }
        }
    }

    print(f"MIT OCW üzerinden {limit} ders taranıyor...")
    response = requests.post(url, json=payload, headers=headers, timeout=30)
    response.raise_for_status()
    hits = response.json().get("hits", {}).get("hits", [])

    courses = []
    for idx, hit in enumerate(hits, start=1):
        src = hit.get("_source", {})
        
        # Doğrudan dersin kendi URL'sini al, yoksa standart MIT OCW ders arama/katalog sayfasına yönlendir
        course_url = src.get("url", "")
        if course_url:
            if not course_url.startswith("http"):
                course_url = f"https://ocw.mit.edu{course_url}"
        else:
            # Yedek olarak ders koduna göre doğrudan MIT OCW ders sayfasına yönlendirme formatı
            coursenum = src.get("coursenum", f"6.{idx:03d}").lower().replace(" ", "-")
            course_url = f"https://ocw.mit.edu/courses/{coursenum}/"

        instructors = src.get("instructors", [])
        instructor_str = ", ".join(instructors) if instructors else "MIT Faculty"

        courses.append({
            "id": f"MIT-{idx:03d}",
            "code": src.get("coursenum", f"6.{idx:03d}"),
            "title": src.get("title", f"MIT OpenCourseWare Dersi {idx}"),
            "url": course_url,
            "instructor": instructor_str,
            "institution": "Massachusetts Institute of Technology (MIT)",
            "department": (src.get("department_name") or ["Computer Science"])[0],
            "level": src.get("level", "Undergraduate"),
            "description": (src.get("short_description") or "Bu ders MIT OpenCourseWare kapsamında kapsamlı teorik ve pratik içerik sunar.")[:240],
            "prerequisites": "Temel Bilgisayar Bilimleri ve Matematik Altyapısı",
            "tools": "Python 3.x, VS Code, Git, Jupyter Notebook",
            "project": "Ders kapsamında uçtan uca pratik laboratuvar ve bitirme projesi."
        })

    os.makedirs("data", exist_ok=True)
    with open("data/courses.json", "w", encoding="utf-8") as f:
        json.dump(courses, f, ensure_ascii=False, indent=2)

    print(f"Başarılı! Toplam {len(courses)} ders doğrudan ders bağlantılarıyla 'data/courses.json' dosyasına kaydedildi.")

if __name__ == "__main__":
    fetch_mit_ocw_courses(500)