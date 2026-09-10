% Reverse-engineering derivation of one generated case into the catalogue.
%
% Model facts (from catalogue.json):
%   family(F). fam_out(F,Role). fam_in(F,Role). fam_op(F,Op). comp(C). axis_val(A,Val).
%   vrule(V). bfield(B). proof(P). proof_fam(P,F). trig(V,A,Val).
% Case facts (canonical record):
%   deliv(Ing). input(Ing). rel(Id,Kind,From,To). req(Id,Ing). con(Id,Ing). acc(Id,Ing). sit(Ing,GenAxis).
% Accepted bridge atoms:
%   b_out(Ing,Family,Role). b_in(Ing,Role). b_rel(Kind,C). b_req(Ing,Op). b_con(Ing,Target).
%   b_acc(Ing,A15Val). b_sit(Ing,A,Val). b_proof(Ing,P).
% Candidate bridge atoms (propose mode only, last argument = lexical rank): c_out/4 c_in/3 c_rel/3 c_req/3 c_con/3 c_acc/3 c_sit/4 c_proof/3

bridge_out(I,F,R) :- b_out(I,F,R).  { use_out(I,F,R) } :- c_out(I,F,R,_).  bridge_out(I,F,R) :- use_out(I,F,R).
bridge_in(I,R)   :- b_in(I,R).      { use_in(I,R) }    :- c_in(I,R,_).      bridge_in(I,R)   :- use_in(I,R).
bridge_rel(K,C)  :- b_rel(K,C).     { use_rel(K,C) }   :- c_rel(K,C,_).     bridge_rel(K,C)  :- use_rel(K,C).
bridge_req(I,O)  :- b_req(I,O).     { use_req(I,O) }   :- c_req(I,O,_).     bridge_req(I,O)  :- use_req(I,O).
bridge_con(I,T)  :- b_con(I,T).     { use_con(I,T) }   :- c_con(I,T,_).     bridge_con(I,T)  :- use_con(I,T).
bridge_acc(I,V)  :- b_acc(I,V).     { use_acc(I,V) }   :- c_acc(I,V,_).     bridge_acc(I,V)  :- use_acc(I,V).
bridge_sit(I,A,V):- b_sit(I,A,V).   { use_sit(I,A,V) } :- c_sit(I,A,V,_).   bridge_sit(I,A,V):- use_sit(I,A,V).
bridge_proof(I,P):- b_proof(I,P).   { use_proof(I,P) } :- c_proof(I,P,_).   bridge_proof(I,P):- use_proof(I,P).

% deliverables: one output role of one family each
{ realize(D,R,F) : bridge_out(D,F,R), fam_out(F,R) } 1 :- deliv(D).
realized(D) :- realize(D,_,_).
unexplained(deliverable,D) :- deliv(D), not realized(D).
in_chain(F) :- realize(_,_,F).

% suppliers join only to feed an input role of a realizing family (one level, at most four)
realizing(F) :- realize(_,_,F).
#const max_suppliers = 4.
#const recursive_suppliers = 0.
{ supply(G,F,R) } :- family(G), fam_out(G,R), fam_in(F,R), realizing(F), G != F, not realizing(G).
{ supply(G,F,R) } :- recursive_suppliers = 1, family(G), fam_out(G,R), fam_in(F,R), in_chain(F), G != F, not realizing(G).
in_chain(G) :- supply(G,_,_).
:- #count{ G : supply(G,_,_) } > max_suppliers.

% input roles resolve from case inputs or from chain producers
resolved(F,R) :- in_chain(F), fam_in(F,R), input(I), bridge_in(I,R).
resolved(F,R) :- in_chain(F), fam_in(F,R), in_chain(G), G != F, fam_out(G,R), grounded(G).
open_input(F,R) :- in_chain(F), fam_in(F,R), not resolved(F,R).
grounded(F) :- resolved(F,_).
unexplained(grounding,F) :- in_chain(F), not grounded(F).
% grounding is well-founded: a chain bottoms out at case inputs; a supplier never joins ungrounded
:- supply(G,_,_), not grounded(G).

% every case input is consumed by a chain family
consumed(I) :- input(I), bridge_in(I,R), in_chain(F), fam_in(F,R).
unexplained(input,I) :- input(I), not consumed(I).

% relationships map to composition forms, both endpoints explained
{ map_rel(Id,C) : bridge_rel(K,C) } 1 :- rel(Id,K,_,_).
unexplained(relationship,Id) :- rel(Id,_,_,_), not map_rel(Id,_).
explained_ing(I) :- realized(I).
explained_ing(I) :- consumed(I).
explained_ing(I) :- req(Id,I), map_req(Id,_,_).
explained_ing(I) :- con(Id,I), map_con(Id,_).
explained_ing(I) :- acc(Id,I), map_acc(Id,_).
explained_ing(I) :- map_sit(I,_,_).
unexplained(endpoint,X) :- rel(_,_,X,_), not explained_ing(X).
unexplained(endpoint,X) :- rel(_,_,_,X), not explained_ing(X).

% requirements map to an operation class performed by a chain family
{ map_req(Id,O,F) : bridge_req(I,O), in_chain(F), fam_op(F,O) } 1 :- req(Id,I).
unexplained(requirement,Id) :- req(Id,_), not map_req(Id,_,_).

% global constraints map to a boundary field, a variation rule or the global invariant claim
{ map_con(Id,T) : bridge_con(I,T) } 1 :- con(Id,I).
unexplained(constraint,Id) :- con(Id,_), not map_con(Id,_).

% acceptance conditions map to an assurance-claim value, with a qualifying operation in the chain
{ map_acc(Id,V) : bridge_acc(I,V) } 1 :- acc(Id,I).
unexplained(acceptance,Id) :- acc(Id,_), not map_acc(Id,_).
has_qualifier :- in_chain(F), fam_op(F,"O16").
unexplained(acceptance_qualifier,chain) :- acc(_,_), not has_qualifier.

% situation ingredients map to axis values
{ map_sit(I,A,V) : bridge_sit(I,A,V) } 1 :- sit(I,_).
unexplained(situation,I) :- sit(I,_), not map_sit(I,_,_).

% variation rules triggered by mapped axis values, by constraint mappings, or by a multi-family chain
vrule_on(V) :- map_sit(_,A,Val), trig(V,A,Val).
vrule_on(V) :- map_con(_,V), vrule(V).
vrule_on(V) :- map_sit(_,"V",V).
vrule_on("V12") :- #count{ F : in_chain(F) } > 1.

% proof layer: each chain family needs an anchoring record bridged from a case ingredient
case_ing(I) :- deliv(I).  case_ing(I) :- req(_,I).  case_ing(I) :- input(I).  case_ing(I) :- acc(_,I).
{ anchor(F,P) : bridge_proof(I,P), proof_fam(P,F), case_ing(I) } 1 :- realizing(F).
proof_gap(F) :- realizing(F), not anchor(F,_).
% supplier families are used generically to feed a role; their family-level anchors cover that use

% costs: explain first, then reuse accepted bridge atoms over new ones, then keep chains small
#minimize { 100@3,K,X : unexplained(K,X) }.
% a candidate atom costs by its lexical rank (1 = best); accepted atoms cost nothing
#minimize { 10*K@2,I,F,R : use_out(I,F,R), c_out(I,F,R,K); 10*K@2,I,R : use_in(I,R), c_in(I,R,K);
            10*K@2,K2,C : use_rel(K2,C), c_rel(K2,C,K); 10*K@2,I,O : use_req(I,O), c_req(I,O,K);
            10*K@2,I,T : use_con(I,T), c_con(I,T,K); 10*K@2,I,V : use_acc(I,V), c_acc(I,V,K);
            10*K@2,I,A,V : use_sit(I,A,V), c_sit(I,A,V,K); 10*K@2,I,P : use_proof(I,P), c_proof(I,P,K) }.
#minimize { 5@1,F : proof_gap(F); 2@1,F,R : open_input(F,R); 1@1,G : supply(G,_,_) }.

#show realize/3. #show supply/3. #show in_chain/1. #show open_input/2. #show unexplained/2.
#show map_rel/2. #show map_req/3. #show map_con/2. #show map_acc/2. #show map_sit/3. #show vrule_on/1.
#show anchor/2. #show proof_gap/1.
#show use_out/3. #show use_in/2. #show use_rel/2. #show use_req/2. #show use_con/2. #show use_acc/2. #show use_sit/3. #show use_proof/2.
