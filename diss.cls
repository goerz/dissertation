%Based on Dissertate Class
% https://github.com/suchow/Dissertate
%Copyright (c) 2014 Jordan Suchow (suchow@post.harvard.edu)
%
%The MIT License (MIT)
%
%Copyright (c) 2014 Michael Goerz (goerz@physik.uni-kassel.de)
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
\LoadClass[12pt]{extbook}

\usepackage[utf8]{inputenc}

% some definitions
\def\degreeyear#1{\gdef\@degreeyear{#1}}
\def\degreemonth#1{\gdef\@degreemonth{#1}}
\def\degreemonthDe#1{\gdef\@degreemonthDe{#1}}
\def\submitDateDe#1{\gdef\@submitDateDe{#1}}
\def\submitDateEn#1{\gdef\@submitDateEn{#1}}
\def\defendDateDe#1{\gdef\@defendDateDe{#1}}
\def\defendDateEn#1{\gdef\@defendDateEn{#1}}
\def\degree#1{\gdef\@degree{#1}}
\def\advisor#1{\gdef\@advisor{#1}}
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
\def\pdOneName#1{\gdef\@pdOneName{#1}}
\def\pdOneSchool#1{\gdef\@pdOneSchool{#1}}
\def\pdOneYear#1{\gdef\@pdOneYear{#1}}
\def\pdTwoName#1{\gdef\@pdTwoName{#1}}
\def\pdTwoSchool#1{\gdef\@pdTwoSchool{#1}}
\def\pdTwoYear#1{\gdef\@pdTwoYear{#1}}
\def\authorDoBen#1{\gdef\@authorDoBen{#1}}
\def\authorDoBde#1{\gdef\@authorDoBde{#1}}
\def\authorPoB#1{\gdef\@authorPoB{#1}}

\RequirePackage{color}
\usepackage{hyperref}
\RequirePackage[md, sc]{titlesec}
\setlength{\headheight}{15pt}
\pagestyle{plain}
\RequirePackage{titling}
\RequirePackage[palatino]{quotchap}

\RequirePackage{kvoptions}
\DeclareStringOption{School}[]
\ProcessKeyvalOptions*
\RequirePackage{packages/\diss@School/style}

\RequirePackage{graphicx}
\RequirePackage{lettrine}
\RequirePackage[comma,numbers]{natbib}
%\renewcommand{\bibnumfmt}[1]{[#1]}
\RequirePackage[width=13.5cm, a4paper]{geometry}
\RequirePackage{fancyhdr}

\usepackage[titletoc]{appendix}
\renewcommand{\setthesection}{\arabic{chapter}.A\arabic{section}}

\RequirePackage{setspace}
\RequirePackage{booktabs}
\RequirePackage[tight,nice]{units}
\RequirePackage{verbatim}
\setcounter{tocdepth}{1}

\RequirePackage{url}
\usepackage[titles]{tocloft}
\renewcommand{\cftsecleader}{\cftdotfill{\cftdotsep}}
\renewcommand{\cftchapfont}{\normalsize \scshape}
\usepackage{fixltx2e}
\usepackage{ragged2e}

\renewcommand\bibname{References}
\renewcommand\listfigurename{Listing of figures}
%\RaggedRight

\parindent 12pt

\widowpenalty=300
\clubpenalty=300

\RequirePackage[labelfont={bf,sf,footnotesize,singlespacing},
								textfont={footnotesize,singlespacing},
								justification={justified,RaggedRight},
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

