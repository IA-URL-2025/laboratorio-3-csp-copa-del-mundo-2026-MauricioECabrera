import copy

class WorldCupCSP:
    def __init__(self, teams, groups, debug=False):
        self.teams = teams
        self.groups = groups
        self.debug = debug

        self.variables = list(teams.keys())
        self.domains = {team: list(groups) for team in self.variables}

    def get_team_confederation(self, team):
        return self.teams[team]["conf"]

    def get_team_pot(self, team):
        return self.teams[team]["pot"]

    def normalize_conf(self, conf):
        if isinstance(conf, list):
            return conf
        return [conf]

    def is_valid_assignment(self, group, team, assignment):
        teams_in_group = [t for t, g in assignment.items() if g == group]

        if len(teams_in_group) >= 4:
            return False

        team_pot = self.get_team_pot(team)
        for t in teams_in_group:
            if self.get_team_pot(t) == team_pot:
                return False

        team_confs = self.normalize_conf(self.get_team_confederation(team))

        conf_counts = {}

        for t in teams_in_group:
            confs = self.normalize_conf(self.get_team_confederation(t))
            for c in confs:
                conf_counts[c] = conf_counts.get(c, 0) + 1

        for conf in team_confs:
            current = conf_counts.get(conf, 0)

            if conf == "UEFA":
                if current >= 2:
                    return False
            else:
                if current >= 1:
                    return False

        return True

    def forward_check(self, assignment, domains):
        new_domains = copy.deepcopy(domains)

        for team in self.variables:
            if team in assignment:
                continue

            valid_groups = []

            for group in new_domains[team]:
                if self.is_valid_assignment(group, team, assignment):
                    valid_groups.append(group)

            new_domains[team] = valid_groups

            if len(valid_groups) == 0:
                new_domains[team] = []
                return False, new_domains

        return True, new_domains

    def select_unassigned_variable(self, assignment, domains):
        unassigned_vars = [v for v in self.variables if v not in assignment]

        if not unassigned_vars:
            return None

        return min(unassigned_vars, key=lambda var: len(domains[var]))

    def backtrack(self, assignment, domains=None):
        if domains is None:
            domains = copy.deepcopy(self.domains)

        if len(assignment) == len(self.variables):
            return assignment

        var = self.select_unassigned_variable(assignment, domains)

        for value in domains[var]:
            if self.is_valid_assignment(value, var, assignment):

                assignment[var] = value

                if self.debug:
                    print(f"Asignando {var} → {value}")

                success, new_domains = self.forward_check(assignment, domains)

                if success:
                    result = self.backtrack(assignment, new_domains)
                    if result is not None:
                        return result

                if self.debug:
                    print(f"Backtracking {var} ← {value}")

                del assignment[var]

        return None