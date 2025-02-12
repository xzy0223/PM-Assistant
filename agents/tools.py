class ResourceQueryTool:
    name: str = "Resource Query Tool"
    description: str = """
    Query technical resource information including developers, teams, and upcoming changes.
    Useful for understanding resource availability and planning project timelines.
    
    Input should be in the format:
    query_type|filter_by|filter_value
    
    Examples:
    - developers||  (Query all developers)
    - developers|skills|Python  (Find developers with Python skills)
    - teams||  (Check all teams)
    - teams|expertise|Backend  (Find teams with Backend expertise)
    - upcoming_changes||  (View all upcoming changes)
    """

    # Mock data for technical resources
    MOCK_RESOURCES = {
        "developers": [
            {
                "id": "dev1",
                "name": "John Smith",
                "role": "Senior Backend Developer",
                "skills": ["Python", "Java", "AWS", "Microservices"],
                "availability": "50%",
                "current_project": "Authentication Service",
                "end_date": "2025-03-15"
            },
            {
                "id": "dev2",
                "name": "Alice Johnson",
                "role": "Frontend Developer",
                "skills": ["React", "TypeScript", "CSS", "UI/UX"],
                "availability": "100%",
                "current_project": None,
                "end_date": None
            },
            {
                "id": "dev3",
                "name": "Bob Wilson",
                "role": "DevOps Engineer",
                "skills": ["Kubernetes", "Docker", "CI/CD", "AWS"],
                "availability": "25%",
                "current_project": "Cloud Migration",
                "end_date": "2025-04-30"
            }
        ],
        "teams": [
            {
                "id": "team1",
                "name": "Core Platform Team",
                "size": 5,
                "current_capacity": "70%",
                "expertise": ["Backend", "Cloud", "DevOps"],
                "current_projects": ["Authentication Service", "API Gateway"]
            },
            {
                "id": "team2",
                "name": "Frontend Team",
                "size": 4,
                "current_capacity": "90%",
                "expertise": ["Frontend", "UI/UX", "Mobile"],
                "current_projects": ["Mobile App Redesign"]
            }
        ],
        "upcoming_changes": [
            {
                "type": "New Hire",
                "role": "Senior Frontend Developer",
                "start_date": "2025-03-01"
            },
            {
                "type": "Team Expansion",
                "team": "Core Platform Team",
                "additional_headcount": 2,
                "target_date": "2025-04-01"
            }
        ]
    }

    def _execute(self, input_str: str) -> str:
        try:
            # Parse input
            parts = input_str.split('|')
            query_type = parts[0]
            filter_by = parts[1] if len(parts) > 1 and parts[1] else None
            filter_value = parts[2] if len(parts) > 2 and parts[2] else None

            # Get base data
            data = self.MOCK_RESOURCES.get(query_type, [])
            
            # Apply filters if provided
            if filter_by and filter_value:
                if query_type == "developers":
                    if filter_by == "skills":
                        data = [dev for dev in data if filter_value in dev["skills"]]
                    elif filter_by == "availability":
                        # Convert percentage string to number for comparison
                        min_availability = float(filter_value.rstrip("%"))
                        data = [dev for dev in data if float(dev["availability"].rstrip("%")) >= min_availability]
                    elif filter_by == "role":
                        data = [dev for dev in data if filter_value.lower() in dev["role"].lower()]
                elif query_type == "teams":
                    if filter_by == "expertise":
                        data = [team for team in data if filter_value in team["expertise"]]
                    elif filter_by == "capacity":
                        min_capacity = float(filter_value.rstrip("%"))
                        data = [team for team in data if float(team["current_capacity"].rstrip("%")) >= min_capacity]
            
            # Format response
            if not data:
                return "No resources found matching the criteria."
            
            return str(data)
            
        except Exception as e:
            return f"Error querying resources: {str(e)}"
