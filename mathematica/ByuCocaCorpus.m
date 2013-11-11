(* ::Package:: *)

(************************************************************************)
(* This file was generated automatically by the Mathematica front end.  *)
(* It contains Initialization cells from a Notebook file, which         *)
(* typically will have the same name as this file except ending in      *)
(* ".nb" instead of ".m".                                               *)
(*                                                                      *)
(* This file is intended to be loaded into the Mathematica kernel using *)
(* the package loading commands Get or Needs.  Doing so is equivalent   *)
(* to using the Evaluate Initialization Cells menu command in the front *)
(* end.                                                                 *)
(*                                                                      *)
(* DO NOT EDIT THIS FILE.  This entire file is regenerated              *)
(* automatically each time the parent Notebook file is saved in the     *)
(* Mathematica front end.  Any changes you make to this file will be    *)
(* overwritten.                                                         *)
(************************************************************************)



BeginPackage["ByuCocaCorpus`",{"DatabaseLink`"}]

ByuCocaPQuery::usage="Later"
ByuCocaC1Query::usage="Later"
ByuCocaC2Query::usage="Later"
ByuCocaSuperintervalQuery::usage="Later"

Begin["`Private`"]

(* used for ensuring that input to a function is always a list *)
makeList[x_List]:=x;
makeList[x_]:={x};

genConnection[host_,credentials_]:=genConnection[host,credentials]=
OpenSQLConnection[
JDBC["PostgreSQL",host],
"Username"->First[credentials],
"Password"->Last[credentials]
];

genTableName[dataset_,NFull_,n_]:=genTableName[dataset,NFull,n]=
"byu_coca_corpus."<>
"\""<>ToString[NFull]<>"gram_"<>dataset<>
"_"<>ToString[n]<>"\"";

genColumnNames[n_]:=genColumnNames[n]=Map["w"<>ToString[#1]&,Range[n]];

(* generic function to select rows from a table *)
selectRows[conn_,table_,cols_,cFuns_,cCols_,cVals_]:=
selectRows[conn,table,cols,cFuns,cCols,cVals]=
SQLSelect[
conn,
table,
cols,
Apply[And, MapThread[#1[SQLColumn[#2],#3]&,{cFuns,cCols,cVals}]]
];

(* selects p, c1 & c2 columns for a given sequence *)
selectSequenceStats[conn_,dataset_,NFull_,S_]:=selectRows[
conn,
genTableName[dataset,NFull,Length[S]],
{"p","c1","c2"},
Table[Equal,{Length[S]}],
genColumnNames[Length[S]],
S
];

(* gets specified statistics for a row assumed to represent a single sequence, throws exceptions if 0 or more than 1 row is given *)
getSequenceStat[{},_]:=Throw[Null,"No rows"];
getSequenceStat[rows_List,i_]:=If[
Length[rows]==1,
Flatten[rows][[i]],
Throw[Null,"Multiple rows"]
];

(* cuts condition part of the query to match order of the model *)
fitS[S_,NFull_]:=Take[S,-Min[Length[S],NFull-1]];
fitS[s_,S_,NFull_]:=
If[
Length[s]>NFull,
Throw[Null,"Cannot submit query of order higher than the model."],
Take[S,-Min[Length[S],NFull]]
]

(* queries database directly for a conditional probability of a sequence, will throw exceptions if the respective n-grams aren't in the database *)
rawP[conn_,dataset_,NFull_,s_,S_,_]:=getSequenceStat[selectSequenceStats[conn,dataset,NFull,Join[S,s]],1]/getSequenceStat[selectSequenceStats[conn,dataset,NFull,S],1];

(* queries database directly for a comulative conditional probability of a sequence, will throw exceptions if the respective n-grams aren't in the database *)
rawC[conn_,dataset_,NFull_,s_,S_,cIndex_]:=
Module[{C1,P,c},
{P,C1}=getSequenceStat[selectSequenceStats[conn,dataset,NFull,S],{1,2}];
c=getSequenceStat[selectSequenceStats[conn,dataset,NFull,Join[S,s]],cIndex+1];
(c-C1)/P
];

(* queries database for a given conditional probability, reduces the context if necessary *)
statQuery[conn_,dataset_,NFull_,s_,S_,rawFun_,cIndex_:Null]:=Catch[
rawFun[conn,dataset,NFull,s,S,cIndex],
"No rows",
Function[{value,tag},
If[Length[S]==0,
Throw[Null,"Cannot decrease order of the query condition any more."],
statQuery[conn,dataset,NFull,s,Rest[S],rawFun,cIndex]
]
]
];

(* final conditional probability functions with automatically reduced context *)
p[conn_,dataset_,NFull_,s_,S_]:=statQuery[conn,dataset,NFull,s,S,rawP,Null]
c1[conn_,dataset_,NFull_,s_,S_]:=statQuery[conn,dataset,NFull,s,S,rawC,1]
c2[conn_,dataset_,NFull_,s_,S_]:=statQuery[conn,dataset,NFull,s,S,rawC,2]

(*getWord[{}]:=Null;
getWord[rows_List]:=BlockRandom[
SeedRandom[10];
First[RandomChoice[rows]]
];

getSuperinterval[conn_,table_,col_,c1_,c2_]:=
getWord[selectRows[
conn,table,col,
{LessEqual,GreaterEqual},{"c1","c2"},{c1,c2}
]];

getSubinterval[conn_,table_,col_,c1_,c2_]:=
getWord[selectRows[
conn,table,col,
{GreaterEqual,LessEqual},{"c1","c2"},{c1,c2}
]];

getPreinterval[conn_,table_,col_,c1_]:=
Flatten[selectRows[
conn,table,{col,"c2"},
{LessEqual,GreaterEqual},{"c1","c2"},{c1,c1}
]];

getPostinterval[conn_,table_,col_,c2_]:=
Flatten[selectRows[
conn,table,{col,"c1"},
{LessEqual,GreaterEqual},{"c1","c2"},{c2,c2}
]];

checkPrevious[conn_,dataset_,NFull_,SCut_]:=
checkPrevious[conn,dataset,NFull,SCut,selectSequenceStats[conn,dataset,NFull,SCut]];
checkPrevious[conn_,dataset_,NFull_,SCut_,{}]:=
checkPrevious[conn,dataset,NFull,Rest[SCut]];
checkPrevious[conn_,dataset_,NFull_,SCut_,result_]:=result;

rawMatchingIntervalQuery[conn_,dataset_,NFull_,v_,S_]:=Module[{},
table=genTableName[dataset,NFull,Length[S]+1];
col="w"<>ToString[Length[SCut]+1];


];

\[Psi][conn_,dataset_,NFull_,v_,S_]:=Module[{table,col,P,C1,c1,c2,s,statRow},
table=genTableName[dataset,NFull,Length[S]+1];
col="w"<>ToString[Length[SCut]+1];

statRow=checkPrevious[conn,dataset,NFull,S];
Print[statRow];

{P,C1}=getSequenceStat[statRow,{1,2}];
{c1,c2}={Floor[C1+P*First[v]],Ceiling[C1+P*Total[v]]};

s=getSuperinterval[conn,table,col,c1,c2];
If[s\[Equal]Null,s=getSubinterval[conn,table,col,c1,c2]];
If[s\[Equal]Null,Throw["Couldn't find a superinterval."]];

Print[Append[S,s]];

s
]*)

ByuCocaPQuery[host_,credentials_,dataset_,NFull_]:=Function[{s,S},
p[
genConnection[host,credentials],
dataset,
NFull,
makeList[s],
fitS[makeList[s],makeList[S],NFull]
]
];

ByuCocaC1Query[host_,credentials_,dataset_,NFull_]:=Function[{s,S},
c1[
genConnection[host,credentials],
dataset,
NFull,
makeList[s],
fitS[makeList[s],makeList[S],NFull]
]
];

ByuCocaC2Query[host_,credentials_,dataset_,NFull_]:=Function[{s,S},
c2[
genConnection[host,credentials],
dataset,
NFull,
makeList[s],
fitS[makeList[s],makeList[S],NFull]
]
];

(*ByuCocaSuperintervalQuery[host_,credentials_,dataset_,NFull_]:=Function[{v,S},
SuperintervalQuery[
genConnection[host,credentials],
dataset,
NFull,
v,
fitS[S,NFull]
]
];*)

End[]

EndPackage[]
