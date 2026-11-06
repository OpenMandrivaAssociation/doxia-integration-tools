Name:		doxia-integration-tools
Version:	2.0.0
Release:	1
Summary:	Tools for using Doxia site rendering inside Maven
Group:		Development/Java
License:	ASL 2.0
URL:		https://maven.apache.org/doxia/doxia-sitetools/
Source0:	https://github.com/apache/maven-doxia-sitetools/archive/refs/tags/doxia-sitetools-%{version}.tar.gz#/doxia-sitetools-%{version}.tar.gz
BuildArch:	noarch
BuildRequires:	python
BuildRequires:	mvn(org.apache.maven.reporting:maven-reporting-api)
BuildRequires:	mvn(javax.inject:javax.inject)
BuildRequires:	mvn(org.slf4j:slf4j-api)
BuildRequires:	mvn(commons-io:commons-io)
BuildRequires:	mvn(org.apache.maven:maven-artifact)
BuildRequires:	mvn(org.apache.maven:maven-core)
BuildRequires:	mvn(com.google.inject:guice-parent:pom::)
BuildRequires:	mvn(org.slf4j:slf4j-parent:pom::)
BuildRequires:	mvn(org.codehaus.plexus:plexus-containers:pom::)
BuildRequires:	mvn(org.apache.maven:maven-model)
BuildRequires:	mvn(org.apache.maven:maven-resolver-provider)
BuildRequires:	mvn(org.apache.maven.resolver:maven-resolver-api)
BuildRequires:	mvn(org.apache.maven.doxia:doxia-site-model)
BuildRequires:	mvn(org.codehaus.plexus:plexus-i18n)
BuildRequires:	mvn(org.codehaus.plexus:plexus-utils)
BuildRequires:	mvn(org.codehaus.plexus:plexus-interpolation)
# Literal, so the first rpmbuild -bs records them before sysjar is installed.
BuildRequires:	maven
BuildRequires:	java-current-devel
BuildSystem:	maven
BuildOption(install):	--file-name %{name}

%description
SiteTool and the decoration reader used by Maven reporting plugins.
The site model supplies the generated decoration classes. XML classes
come from plexus-utils, so this build does not use plexus-xml.

%prep
%autosetup -n maven-doxia-sitetools-doxia-sitetools-%{version}
rm -rf src
mv doxia-integration-tools/src src
python - <<'PY'
import xml.etree.ElementTree as ET
NS = "http://maven.apache.org/POM/4.0.0"
ET.register_namespace("", NS)

def tag(name):
    return "{" + NS + "}" + name

def add(parent, name, text):
    node = ET.SubElement(parent, tag(name))
    node.text = text
    return node

root = ET.Element(tag("project"))
add(root, "modelVersion", "4.0.0")
add(root, "groupId", "org.apache.maven.doxia")
add(root, "artifactId", "doxia-integration-tools")
add(root, "version", "%{version}")
add(root, "name", "Doxia Sitetools :: Integration Tools")
deps = ET.SubElement(root, tag("dependencies"))
for group, artifact, version, scope in (
    ("org.apache.maven.reporting", "maven-reporting-api", "4.0.0", ""),
    ("javax.inject", "javax.inject", "1", ""),
    ("org.slf4j", "slf4j-api", "1.7.36", ""),
    ("commons-io", "commons-io", "2.22.0", ""),
    ("org.apache.maven", "maven-artifact", "3.10.0", "provided"),
    ("org.apache.maven", "maven-core", "3.10.0", "provided"),
    ("org.apache.maven", "maven-model", "3.10.0", "provided"),
    ("org.apache.maven", "maven-resolver-provider", "3.10.0", "provided"),
    ("org.apache.maven.resolver", "maven-resolver-api", "2.0.24", "provided"),
    ("org.apache.maven.doxia", "doxia-site-model", "%{version}", ""),
    ("org.codehaus.plexus", "plexus-i18n", "1.2.0", ""),
    ("org.codehaus.plexus", "plexus-utils", "3.6.0", ""),
    ("org.codehaus.plexus", "plexus-interpolation", "1.27", ""),
):
    dep = ET.SubElement(deps, tag("dependency"))
    add(dep, "groupId", group)
    add(dep, "artifactId", artifact)
    add(dep, "version", version)
    if scope:
        add(dep, "scope", scope)
ET.ElementTree(root).write("pom.xml", encoding="utf-8", xml_declaration=True)
PY
# Sisu loads @Named classes from this index. The indexer plugin is not packaged.
python - <<'PY'
import re
from pathlib import Path
root = Path("src/main/java")
names = []
for path in sorted(root.rglob("*.java")):
    text = path.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"\b(?:class|interface|enum)\s+([A-Za-z0-9_]+)", text)
    if not match:
        continue
    if "@Named" not in text[:match.start()]:
        continue
    pkg = re.search(r"(?m)^package\s+([A-Za-z0-9_.]+)\s*;", text)
    if not pkg:
        continue
    names.append(pkg.group(1) + "." + match.group(1))
if names:
    dest = Path("src/main/resources/META-INF/sisu")
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "javax.inject.Named").write_text("\n".join(names) + "\n", encoding="utf-8")
PY
rm -rf doxia-integration-tools doxia-site-model doxia-site-renderer doxia-skin-model

%files -f .mfiles
%doc README.md
