import PyPDF2

from rosterReaders.txtroster import RosterReader

path = "C:\\Users\\Xico\\Google Drive\\Sobrecargo\\roles\\201705.pdf"
read_pdf = PyPDF2.PdfFileReader(path)


number_of_pages = read_pdf.getNumPages()
print("number of pages ", number_of_pages)
page = read_pdf.getPage(0)
page_content = page.extractText()
print(page_content)
rr = RosterReader(page_content)
print("crew_stats : ", rr.crew_stats)
print("Carry in within month? ", rr.carry_in)
print("Roster timeZone ", rr.timeZone)
print("Roster year and month ", rr.year, rr.month)