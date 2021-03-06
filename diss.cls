%Based on Dissertate Class
% https://github.com/suchow/Dissertate
%Copyright (c) 2014 Jordan Suchow (suchow@post.harvard.edu)
%
%The MIT License (MIT)
%
%Copyright (c) 2015 Michael Goerz (goerz@physik.uni-kassel.de)
%
%Permission is hereby granted, free of charge, to any person obtaining a copy of
%this software and associated documentation files (the ``Software''), to deal in
%the Software without restriction, including without limitation the rights to
%use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
%the Software, and to permit persons to whom the Software is furnished to do so,
%subject to the following conditions:
%
%The above copyright notice and this permission notice shall be included in all
%copies or substantial portions of the Software.
%
%THE SOFTWARE IS PROVIDED ``AS IS'', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
%IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
%FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
%COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
%IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
%CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{diss}
\LoadClass[12pt]{book}
%\usepackage{setspace}
%\setstretch{1.1}

\usepackage[utf8]{inputenc}

% some definitions
\def\degreeyear#1{\gdef\@degreeyear{#1}}
\def\degreemonth#1{\gdef\@degreemonth{#1}}
\def\degreemonthDe#1{\gdef\@degreemonthDe{#1}}
\def\submitDateDe#1{\gdef\@submitDateDe{#1}}
\def\defendDateDe#1{\gdef\@defendDateDe{#1}}
\def\degree#1{\gdef\@degree{#1}}
\def\degreeFullDe#1{\gdef\@degreeFullDe{#1}}
\def\degreeFullEn#1{\gdef\@degreeFullEn{#1}}
\def\advisorDe#1{\gdef\@advisorDe{#1}}
\def\advisorEn#1{\gdef\@advisorEn{#1}}
\def\committeeA#1{\gdef\@committeeA{#1}}
\def\committeeB#1{\gdef\@committeeB{#1}}
\def\committeeC#1{\gdef\@committeeC{#1}}
\def\department#1{\gdef\@department{#1}}
\def\keywords#1{\gdef\@keywords{#1}}
\def\field#1{\gdef\@field{#1}}
\def\fieldDe#1{\gdef\@fieldDe{#1}}
\def\university#1{\gdef\@university{#1}}
\def\universitycity#1{\gdef\@universitycity{#1}}
\def\universitystate#1{\gdef\@universitystate{#1}}
\def\programname#1{\gdef\@programname{#1}}
\def\authorPrevDegree#1{\gdef\@authorPrevDegree{#1}}
\def\authorDoBen#1{\gdef\@authorDoBen{#1}}
\def\authorDoBde#1{\gdef\@authorDoBde{#1}}
\def\authorPoB#1{\gdef\@authorPoB{#1}}

\usepackage{calc}

\RequirePackage{graphicx}
\RequirePackage{tabularx}
\RequirePackage{booktabs}
\RequirePackage{amssymb, amsmath, amsfonts, amsthm}
\RequirePackage[comma,numbers]{natbib}
%\renewcommand{\bibnumfmt}[1]{[#1]}

\RequirePackage{xcolor}
\usepackage{hyperref}
\usepackage[raggedright, sf, toctitles]{titlesec}
\pagestyle{plain}
\RequirePackage{titling}
\RequirePackage[palatino]{quotchap} % put large chapter number on top right

\renewcommand*{\sectfont}{\sffamily\huge} % chapter title

\titleformat{\section}
  {\normalfont\raggedright\sffamily\Large}
  {\thesection}{1em}{}

\titleformat{\subsection}
  {\normalfont\raggedright\sffamily\large}
  {\thesubsection}{1em}{}

\university{Universität Kassel}
\universitycity{Kassel}
\universitystate{Germany}
\degree{Dr.~rer.~Nat.}
\degreeFullDe{Doktor der Naturwissenschaften}
\degreeFullEn{Doktor der Naturwissenschaften}

\definecolor{Crimson}{rgb}{0.6471, 0.1098, 0.1882}
\definecolor{chaptergrey}{rgb}{0.6471, 0.1098, 0.1882} % Crimson

\hypersetup{%
    unicode=true,
    colorlinks=false,
    citecolor=black,
    filecolor=black,
    linkcolor=black,
    urlcolor=black,
    bookmarksopen=false,
    breaklinks=true,
    plainpages=false,
    pdfpagelabels,
    hidelinks
}

\renewcommand{\frontmatter}{%
  \input{frontmatter/personalize}
  \hypersetup{%
      pdftitle={\thetitle},
      pdfauthor={\theauthor},
      pdfkeywords={\@keywords},
      pdfsubject={Dissertation, PhD Thesis},
  }
  \makegermantitle
  \copyrightpage
  \cleardoublepage
  \maketitle
  \cleardoublepage
  \germanabstractpage
  \cleardoublepage
  \pdfbookmark{Abstract}{Abstract}
  \abstractpage
  \cleardoublepage
  \pdfbookmark{\contentsname}{Table of Contents}
  \tableofcontents
  \cleardoublepage
  %\pdfbookmark{Listing of figures}{Listing of figures}
  %\listoffigures
  %\cleardoublepage
  \dedicationpage
  \pdfbookmark{Acknowledgments}{Acknowledgments}
  \acknowledgments
  % Setting for the main matter
  \pagenumbering{arabic}
  \setcounter{page}{0}
  \pagestyle{fancy}
  \pagestyle{fancyplain}
  \fancyhf{}
  \fancyhead[LE,RO]{\thepage}
  \fancyhead[LO]{\it \rightmark}
  \fancyhead[RE]{\it \leftmark}
  \fancypagestyle{plain}{%
    \fancyhead{} % get rid of headers
    \renewcommand{\headrulewidth}{0pt} % and the line
    \fancyfoot[C]{\thepage}
  }
}

\newcommand{\makegermantitle}{%
  \thispagestyle{empty}
  \newgeometry{left=\centeredmargin, top=\titletopmargin, right=\centeredmargin,
               bindingoffset=\bindingoffset}
  \begin{center}
  %~\vspace{10pt}~\\
  \Huge \textcolor{Crimson}{\thetitle} \normalsize \\
  \vspace{20pt}
  {\Large
  \textsc{Dissertation}\\
  }
  \large
  \vspace{20pt}
  zur Erlangung des akademischen Grades \\
  \textsc{\@degreeFullDe}\\
  (\@degree) \\
  im Fach \@fieldDe \\
  \vspace{15pt}
  eingereicht am \\
  \@department\\
  \@university \\
  \vspace{15pt}
  von \\
  \vspace{10pt}
  \textbf{\@authorPrevDegree{} \theauthor} \\
  \end{center}
  \vspace{40pt}
  \large
  \begin{center}
  \@advisorDe\\
  \vspace{15pt}
  \ifdefined\@committeeA%
  \@committeeA\\
  \else%
  ~\\
  \fi%
  \ifdefined\@committeeB%
  \@committeeB\\
  \else%
  ~\\
  \fi%
  \vspace{20pt}
  Eingereicht am: \@submitDateDe\\
  \ifdefined\@defendDateDe%
  Disputation am: \@defendDateDe
  \else%
  ~
  \fi%
  \end{center}

  \restoregeometry
}

\renewcommand{\maketitle}{%
  \thispagestyle{empty}
  \newgeometry{left=\centeredmargin, top=\titletopmargin, right=\centeredmargin,
               bindingoffset=\bindingoffset}
  \begin{center}
  %~\vspace{10pt}~\\
  \Huge \textcolor{Crimson}{\thetitle} \normalsize \\
  \vspace{20pt}
  {\Large
  \textsc{Dissertation}\\
  }
  \large
  \vspace{20pt}
  in partial fulfillment of the requirements\\
  for the degree of\\
  \textsc{\@degreeFullEn}\\
  (\@degree) \\
  in the field of \@field \\
  \vspace{15pt}
  submitted to the\\
  \@department\\
  \@university \\
  \vspace{15pt}
  by \\
  \vspace{10pt}
  \textbf{\@authorPrevDegree{} \theauthor} \\
  \vspace{40pt}
  \@advisorEn \\
  \vspace{40pt}
  \@degreemonth{} \@degreeyear
  \end{center}
  \restoregeometry
}

\newcommand{\copyrightpage}{%
  \newpage
  \thispagestyle{empty}
  \vspace*{\fill}
  \scshape \noindent \small \copyright \small \@degreeyear\hspace{3pt}-- \theauthor \\
  \vspace*{\fill}
  \newpage
  \rm
}

\newcommand{\germanabstractpage}{%
  \newpage
  \pagenumbering{roman}
  \setcounter{page}{5}
  \pagestyle{fancy}
  \renewcommand{\headrulewidth}{0.0pt}
  \vspace*{35pt}
  \begin{center}
  \Large \textcolor{Crimson}{\@title} \normalsize \\
  \vspace*{20pt}
  \scshape Zusammenfassung \\ \rm
  \end{center}
  \input{frontmatter/abstract_german}
  \vspace*{\fill}
  \newpage \lhead{} \rhead{}
  \cfoot{\thepage}
}


\newcommand{\abstractpage}{%
  \newpage
  \pagenumbering{roman}
  \setcounter{page}{7}
  \pagestyle{fancy}
  \renewcommand{\headrulewidth}{0.0pt}
  \vspace*{35pt}
  \begin{center}
  \Large \textcolor{Crimson}{\@title} \normalsize \\
  \vspace*{20pt}
  \scshape Abstract \\ \rm
  \end{center}
  \input{frontmatter/abstract}
  \vspace*{\fill}
  \newpage \lhead{} \rhead{}
  \cfoot{\thepage}
}

\newcommand{\dedicationpage}{%
  \newpage \thispagestyle{empty} \vspace*{\fill}
  \scshape \noindent \input{frontmatter/dedication}
  \vspace*{\fill} \newpage \rm
}

\newcommand{\acknowledgments}{%
  \chapter*{Acknowledgments}
  \noindent
  \input{frontmatter/thanks}
  \vspace*{\fill} \newpage
}

\newcommand{\printbib}[2]{%
  \cleardoublepage
  \fancyhf{}
  \fancyhead[LE,RO]{\thepage}
  \fancyhead[LO]{\it References}
  \fancyhead[RE]{\it References}
  \bibliographystyle{#1}
  \bibliography{#2}
  \addcontentsline{toc}{chapter}{References}
}

\newcommand{\printind}{%
  \cleardoublepage
  \fancyhf{}
  \fancyhead[LE,RO]{\thepage}
  \fancyhead[LO]{\it Index}
  \fancyhead[RE]{\it Index}
  \chaptermark{Index}
  \printindex
  \addcontentsline{toc}{chapter}{Index}
}

\renewcommand{\mainmatter}{%
  \renewcommand{\chaptermark}[1]{\markboth{\thechapter.\ ##1}{}}
  \renewcommand{\sectionmark}[1]{\markright{\thesection.\ ##1}}
  \renewcommand{\headrulewidth}{0.5pt} \renewcommand{\footrulewidth}{0pt}
}

% mark the first page as the title page in the PDF bookmarks. This must be
% called immediately after \begin{document}
\newcommand{\marktitlepage}{%
  \pdfbookmark[0]{Title Page}{title}
  \pagenumbering{roman}
  \setcounter{page}{1}
}

\newcommand{\erklaerung}{%
  \cleartoleftpage
  \thispagestyle{empty}
  \vspace*{\fill}

  \begin{flushleft}
  \noindent
  Hiermit versichere ich, dass ich die vorliegende Dissertation selbstständig,
  ohne unerlaubte Hilfe Dritter angefertigt und andere als die in der Dissertation
  angegebenen Hilfsmittel nicht benutzt habe. Alle Stellen, die wörtlich oder
  sinngemäß aus veröffentlichten oder unveröffentlichten Schriften entnommen sind,
  habe ich als solche kenntlich gemacht. Dritte waren an der
  inhaltlich-materiellen Erstellung der Dissertation nicht beteiligt;
  insbesondere habe ich hierfür nicht die Hilfe eines Promotionsberaters in
  Anspruch genommen. Kein Teil dieser Arbeit ist in einem anderen Promotions- oder
  Habilitationsverfahren verwendet worden.
  \end{flushleft}

  \vspace*{20pt}

  \@degreemonthDe{} \@degreeyear, \@universitycity

  \vspace*{70pt}

  \theauthor{}

  \vspace*{10pt}

}

%%%% Page Layout

\usepackage{lmodern}
\usepackage[T1]{fontenc}

% Leading (distance from one baseline to the next)
% Must be chosen appropriately for the main text font size of 12pt
\newlength{\lead}
\setlength{\lead}{14.5pt}
\usepackage{leading}
\leading{\lead}

% Paragraph indentation is also by one lead
\parindent \lead


% A4
\setlength{\paperwidth}{210mm}
\setlength{\paperheight}{297mm}
% Letter
%\setlength{\paperwidth}{8.5in}
%\setlength{\paperheight}{11in}

% Main text block
% Width chosen to allow for 66 characters at font size 12
\setlength{\textwidth}{12.5cm}
\setlength{\textheight}{21.65cm} % Hexagon ratio, 1:sqrt(3)

% We need to account for the binding by adding some extra space on the inner
% edge
\newlength{\bindingoffset}
\setlength{\bindingoffset}{0.8cm}

% top margin and bottom margin are equal
% Note: header/footer are inside the top/bottom margin
\setlength{\topmargin}{(\paperheight-\textheight)/2}

% height of header line (must be at least \head)
\setlength{\headheight}{\lead}

% Inner and outer margins: outer margin should be twice as large as inner margin
% (excluding binding offset) to create an even spacing in two-sided priting
\newlength{\innermargin}
\setlength{\innermargin}{(\paperwidth-\textwidth-\bindingoffset)/3}
% For the title page, we center the contents on the printed page instead
\newlength{\centeredmargin} % margin the centers textblock on the page
\setlength{\centeredmargin}{(\paperwidth-\textwidth-\bindingoffset)/2}
% Also, using topmargin does not work with \thispagestyle{empty}, so we must
% create an alias
\newlength{\titletopmargin}
\setlength{\titletopmargin}{\topmargin}

\RequirePackage[top=\topmargin, inner=\innermargin, width=\textwidth,
                height=\textheight, headsep=2\lead, headheight=\headheight,
                footskip=3\lead, bindingoffset=\bindingoffset,
                paperwidth=\paperwidth, paperheight=\paperheight]{geometry}
\RequirePackage{fancyhdr}

\RequirePackage{lettrine}
% small-caps need slightly increased letter spacing
\usepackage[tracking=smallcaps,expansion=alltext,protrusion=true,verbose=silent]{microtype}
\DeclareMicrotypeAlias{lmss}{cmr}
\SetTracking[spacing={25*,166,}]{encoding=*,shape=sc}{50}

% Table of contents
\usepackage{tocstyle}
\usetocstyle{KOMAlike}
\settocfeature{raggedhook}{\raggedright}
\usepackage[titletoc]{appendix}
\renewcommand{\setthesection}{\arabic{chapter}.A\arabic{section}}

\RequirePackage{setspace}
\RequirePackage{booktabs}
\RequirePackage[tight,nice]{units}
\RequirePackage{verbatim}
\setcounter{tocdepth}{2}

\RequirePackage{url}
\usepackage[titles]{tocloft}
\renewcommand{\cftsecleader}{\cftdotfill{\cftdotsep}}
\renewcommand{\cftchapfont}{\normalsize \scshape}
\usepackage{fixltx2e}
\usepackage{ragged2e}

\renewcommand\bibname{References}
\renewcommand\listfigurename{Listing of figures}
%\RaggedRight

\widowpenalty=300
\clubpenalty=300

\RequirePackage[labelfont={bf,sf,footnotesize,singlespacing},
                textfont={footnotesize,singlespacing},
                justification=raggedright,
                singlelinecheck=false,
                margin=0pt,
                figurewithin=chapter,
                tablewithin=chapter]{caption}

\renewcommand{\thefootnote}{\fnsymbol{footnote}}


% an environment for paragraph-style section
\providecommand\newthought[1]{%
   \addvspace{1.0\baselineskip plus 0.5ex minus 0.2ex}%
   \noindent\textsc{#1}%
}

% Align reference numbers so that they do not cause an indent
\newlength\mybibindent
\setlength\mybibindent{0pt}
\makeatletter
\renewenvironment{thebibliography}[1]
    {\chapter*{\bibname}%
     \@mkboth{\MakeUppercase\bibname}{\MakeUppercase\bibname}%
     \list{\@biblabel{\@arabic\c@enumiv}}
          {\settowidth\labelwidth{\@biblabel{999}}
           \leftmargin\labelwidth
            \advance\leftmargin\dimexpr\labelsep+\mybibindent\relax\itemindent-\mybibindent
           \@openbib@code
           \usecounter{enumiv}
           \let\p@enumiv\@empty
           \renewcommand\theenumiv{\@arabic\c@enumiv}}
     \sloppy
     \clubpenalty4000
     \@clubpenalty \clubpenalty
     \widowpenalty4000%
     \sfcode`\.\@m}
    {\def\@noitemerr
      {\@latex@warning{Empty `thebibliography' environment}}
     \endlist}
\makeatother

% make sure there are no headers/footers on blank page
\makeatletter
    \def\cleardoublepage{\clearpage\if@twoside \ifodd\c@page\else
    \hbox{}
    \vspace*{\fill}
    \thispagestyle{empty}
    \newpage
    \if@twocolumn\hbox{}\newpage\fi\fi\fi}
\makeatother

% Allow to clear to a left page (like \cleardoublepage clears to right page)
\makeatletter
    \def\cleartoleftpage{\clearpage\if@twoside \ifodd\c@page
    \hbox{}
    \vspace*{\fill}
    \thispagestyle{empty}
    \newpage
    \if@twocolumn\hbox{}\newpage\fi\fi\fi}
\makeatother

