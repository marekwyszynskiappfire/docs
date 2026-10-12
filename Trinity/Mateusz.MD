**Odpowiedzi (EN):** [MATEUSZ-POC-ANSWERS.md](MATEUSZ-POC-ANSWERS.md) · **Backlog GitHub:** [GITHUB-BACKLOG.md](GITHUB-BACKLOG.md)

1. POC Test Case Generatora — termin: 14/10
Do 14/10 powinno być dostępne działające rozwiązanie, które:
generuje test scenarios / test cases na podstawie zadanego inputu;
zapisuje wygenerowane Test Cases bezpośrednio do Xray na Jira PROD, do wydzielonego projektu testowego;
działa jako agent, skill lub workflow gotowy do praktycznego użycia;
pozwala kontrolować strukturę i poziom szczegółowości generowanych testów.
Samo pokazanie, że AI potrafi wygenerować testy, nie jest wystarczające. Musimy również pokazać, w jaki sposób kontrolujemy:
granulację Test Cases;
jakość wygenerowanego outputu;
spójność i powtarzalność wyników;
utrzymywalność testów w dłuższym okresie; - pokazać jak będziemy mierzyć
zgodność ze standardami projektu / zespołu;
zakres wymaganej interwencji człowieka.
2. Evidence / scorecard
Dla Test Case Generatora powinien powstać one pager scorecard
Scorecard powinien zawierać minimum:
Use case — jaki problem rozwiązujemy;
Product / solution — czego dokładnie użyto;
Who used it — kto faktycznie korzystał z rozwiązania;
Input — jakie dane / wymagania zostały przekazane do AI;
Output — co zostało wygenerowane;
Human review — kto i jak zweryfikował rezultat;
Accepted / Rejected — co zostało zaakceptowane, a co odrzucone;
Impact — wpływ na czas, jakość lub koszt;


3. Metryki wymagane dla Test Case Generatora
Musimy mierzyć co najmniej:
liczbę AI-generated Test Cases;
liczbę AI-generated Test Cases zaakceptowanych po human review;
liczbę AI-generated Test Cases odrzuconych;
acceptance rate;
powody odrzucenia Test Cases, np.:
zbyt wysoka / zbyt niska granulacja,
duplikaty,
brakujące scenariusze,
niepoprawne założenia,
słaba jakość kroków lub expected results,
brak zgodności z wymaganiami,
problemy z utrzymywalnością;
czas potrzebny na wygenerowanie i review Test Cases;
porównanie do procesu wykonywanego bez AI, tam gdzie jest to możliwe.
Celem jest pokazanie nie tylko wolumenu generowanych testów, ale przede wszystkim ile z nich jest rzeczywiście użytecznych po review i dlaczego.
4. Dokumentacja i dashboardy — termin końcowy: 16/10
Najpóźniej do 16/10 całość powinna obejmować:
działające rozwiązanie;
dokumentację opisującą:
architekturę / workflow,
sposób użycia,
wymagany input,
sposób konfiguracji,
zasady kontroli jakości,
zasady human review,
sposób kontroli granulacji,
znane ograniczenia;
Scorecard dla TC Generatora
Prekonfigurowane dashboardy zbierające wymagane metryki i evidence;



5. Walidacja w wielu projektach
Jeżeli skill / agent / workflow jest już gotowy do użycia, nie powinniśmy czekać do końca POC z jego walidacją.
Należy jak najszybciej uruchomić rozwiązanie w kilku różnych projektach, aby sprawdzić:
czy działa dla różnych typów wymagań;
czy jakość wyników jest powtarzalna;
jakie różnice w konfiguracji są wymagane pomiędzy projektami;
czy przyjęte zasady granulacji są wystarczające;
jakie są najczęstsze przyczyny odrzucenia wygenerowanych testów;
czy rozwiązanie skaluje się poza pojedynczy projekt testowy.
Marek powinien zapewnić, że zadanie nie kończy się na demonstracji technologii.
Oczekiwanym rezultatem jest działające rozwiązanie + rzeczywisty evidence z użycia + mierzalne wyniki + rekomendacja i plan dotycząca dalszego skalowania.
Na koniec powinniśmy być w stanie jednoznacznie odpowiedzieć na pytania:
Czy rozwiązanie działa? 
Czy ludzie faktycznie go użyli?
 Jaki procent outputu został zaakceptowany?
 Dlaczego część została odrzucona?
 Jaki jest wpływ na czas, jakość lub koszt? 
