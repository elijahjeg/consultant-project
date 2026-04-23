import re
from bs4 import BeautifulSoup

CONTAINERS = (
    "div",
    "section",
    "header",
    "main",
    "header",
    "footer",
    "aside",
)


def getClassList(string):
    """Finds the list of classes if it matches the class="" pattern."""
    pattern = re.compile(r'class="([^"]+)"')
    match = pattern.search(string)
    if not match:
        return []
    return match.group(1).split()

def removeStyles(messyTxt):
    """Removes the style attribute completely from all elements with re.sub()"""
    stylePattern = r'(<\s*\w+[^>]*?)\s*(style|id)\s*=\s*"[^"]*"([^>]*>)' # Matches <element style="...">
    return re.sub(stylePattern, r"\1\3", messyTxt)

def removeSpans(messyTxt):
    """Removes all span elements from the HTML with re.sub(), keeping the content inside the span."""
    spanPattern = r'<\s*span[^>]*>(.*?)<\s*/\s*span\s*>'
    return re.sub(spanPattern, r"\1", messyTxt, flags=re.DOTALL)

def filterClasses(messyTxt, classes):
    """Filters the classes so that only the valid classes stay, if none of the classes are valid remove the attribute all together."""
    # Matches any element 
    classPattern = re.compile(r'<\s*\w+[^>]*?\s+(?P<attr>class\s*=\s*"(?P<value>[^"]+)")([^>]*?>)', re.DOTALL)
    newHtml = ""
    last = 0

    # Loop over all matches
    for match in classPattern.finditer(messyTxt):
        # Append the part of the string before the match to the new HTML
        newHtml += messyTxt[last:match.start("attr")].rstrip() # Remove trailing whitespace before the class attribute (since it might be removed)

        last = match.end()
        groupList = match.group("value").split()

        # Filter the classes in the class attribute value
        valid = []
        for i in groupList:
            if i in classes:
                valid.append(i)

        if valid:
            newClassList = f' class="{" ".join(valid)}"'
            newHtml += newClassList
        
        newHtml += messyTxt[match.end("attr"):match.end()]
            

    newHtml += messyTxt[last:]
    return newHtml
    

def findClosingTag(lines, tag):
    """Finds the closing tag for the given tag in the list of lines and returns the index of the line and the match object for the closing tag."""
    pattern = re.compile(fr"<(/)?\s*{tag}\b[^>]*>")
    depth = 0

    for i, line in enumerate(lines):
        if line is not None:
            for match in pattern.finditer(line):
                if match.group(1):
                    if depth == 0:
                        return i, match
                    else:
                        depth -= 1
                else:
                    depth += 1


def write(html):
    """Shorthand function for writing the HTML to a file."""
    with open('cleaned.html', 'w') as cleaned:
        cleaned.write(html)

def unwrapElements(lines, pattern, classes):
    """Unwraps elements that match the pattern and have only one child element or no child elements, and don't have any of the valid classes."""
    for i, line in enumerate(lines):
        if line is None:
            continue

        # Use finditer here because findall only returns a list of strings/tuples
        matches = list(pattern.finditer(line))
        if not matches:
            continue

        match = matches.pop(0)
        if len(matches) > 0:
            originalLen = len(line)
            # Insert the other matches as new lines after the current line, with indentation
            # This prevents multiple matches being on one line and possibly being skipped
            for j, otherMatch in enumerate(matches):
                lines.insert(i+j+1, "    " + otherMatch.group())
                start = otherMatch.start() + len(lines[i]) - originalLen
                end = otherMatch.end() + len(lines[i]) - originalLen
                lines[i] = line = line[:start] + line[end:]

        afterLines = lines[i+1:]
        lastLineIndex, lastLineMatch = findClosingTag(afterLines, match.group(1))

        elementLines = afterLines[:lastLineIndex+1]

        # Use the original line indentation as an offset for the rest
        indent = 0
        for c in lines[i]:
            if c == " ":
                indent += 1


        indexOffset = i+1

        attributeStr = match.group(2)
        if attributeStr:
            intersctedClasses = set(getClassList(attributeStr)) & classes
        else:
            intersctedClasses = None
            
        matchHtml = "\n".join(line for line in lines[i:lastLineIndex+indexOffset+1] if line is not None)
        soup = BeautifulSoup(matchHtml, "html.parser")
        children = soup.find(match.group(1)).contents

        count = 0

        # Loop over the children and count the number of non-empty strings and elements, if there is more than one, we shouldn't unwrap the element
        for child in children:
            if isinstance(child, str):
                if not child.strip():
                    continue
            count += 1

        # If there is only one non-empty string or element and there are no valid classes, we can unwrap the element
        if count <= 1 and not intersctedClasses:
            for j, elementLine in enumerate(elementLines):
                if j == lastLineIndex:
                    elementLine = elementLine[:lastLineMatch.start()] + elementLine[lastLineMatch.end():]
                    if not elementLine.strip():
                        lines[indexOffset+j] = None
                        continue

                if elementLine[:indent+1].isspace():   
                    lines[indexOffset+j] = elementLine[indent:]
            

            lines[i] = line[:match.start()] + line[match.end():]

            if not lines[i].strip():
                lines[i] = None

def cleanHtml(messyTxt, cssTxt):
    """Cleans the provided HTML by removing unused classes and unwrapping unnecessary elements."""
    pattern = re.compile(r"\.([A-Za-z-][\w-]+)")
    classes = set() # Use a set to prevent duplicates and it's faster

    for x in pattern.finditer(cssTxt):
        classes.add(x.group()[1:]) # without the "."

    pattern = re.compile(fr'<\s*({"|".join(CONTAINERS)})\s*([^>]+)?>')
    messyTxt = removeStyles(messyTxt)
    messyTxt = removeSpans(messyTxt)
    messyTxt = filterClasses(messyTxt, classes)
    lines = messyTxt.splitlines()
    unwrapElements(lines, pattern, classes)
    return "\n".join(line for line in lines if line is not None)

def main():
    """Main function that runs the whole process."""
    with (
        open("test/messy.html") as messy, 
        open("test/css.txt") as css
    ):
        messyTxt = messy.read()
        cssTxt = css.read()

    cleanedHtml = cleanHtml(messyTxt, cssTxt)
    write(cleanedHtml)

if __name__ == "__main__":
    main()