from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import json

from app.services.agent.hubspot.account_health_agent.prompts.recommendations import PromptManager, PromptTemplate


@dataclass
class Node:
    id: str
    type: str  # 'deal', 'contact', 'engagement', etc.
    attributes: Dict
    risk_score: float = 0.0


@dataclass
class Edge:
    source_id: str
    target_id: str
    type: str  # 'interaction', 'ownership', 'relationship', etc.
    attributes: Dict
    strength: float = 1.0


class LLMRecommendationEngine:
    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.prompt_manager = PromptManager()

    async def analyze_and_recommend(self, analytics_data: Dict) -> Dict:
        """Generate comprehensive analysis and recommendations."""
        try:
            # Create graph structure for pattern analysis
            nodes, edges = await self.generate_graph_from_analytics(analytics_data)

            # Analyze patterns
            risk_patterns = self._identify_risk_patterns(nodes, edges)
            opportunity_patterns = self._identify_opportunity_patterns(nodes, edges)

            # Prepare context data
            context_data = {
                **self.prompt_manager.format_context(analytics_data),
                'risk_data': json.dumps(risk_patterns, indent=2),
                'opportunity_data': json.dumps(opportunity_patterns, indent=2),
                'graph_metrics': self._calculate_graph_metrics(nodes, edges)
            }

            # Generate different types of analysis
            analyses = await self._generate_analyses(context_data)

            # Combine all insights
            return {
                'recommendations': analyses.get('recommendations', []),
                'risk_analysis': analyses.get('risk_analysis', {}),
                'opportunity_analysis': analyses.get('opportunity_analysis', {}),
                'patterns': {
                    'risks': risk_patterns,
                    'opportunities': opportunity_patterns
                },
                'graph_metrics': context_data['graph_metrics']
            }
        except Exception as e:
            print(f"Error in analyze_and_recommend: {str(e)}")
            return {
                'recommendations': [],
                'risk_analysis': {},
                'opportunity_analysis': {},
                'patterns': {'risks': [], 'opportunities': []},
                'graph_metrics': {}
            }

    async def generate_graph_from_analytics(self, analytics_data: Dict) -> Tuple[List[Node], List[Edge]]:
        """Convert analytics data into a graph structure."""
        nodes = []
        edges = []

        try:
            # Create nodes for deals
            for deal in analytics_data.get('deals', []):
                deal_node = Node(
                    id=f"deal_{deal['id']}",
                    type='deal',
                    attributes={
                        'amount': deal.get('amount'),
                        'stage': deal.get('stage'),
                        'days_in_stage': deal.get('days_in_stage'),
                        'last_activity': deal.get('last_activity_date')
                    },
                    risk_score=self._calculate_deal_risk(deal)
                )
                nodes.append(deal_node)

            # Create nodes for contacts
            for contact in analytics_data.get('contacts', []):
                contact_node = Node(
                    id=f"contact_{contact['id']}",
                    type='contact',
                    attributes={
                        'role': contact.get('role'),
                        'engagement_level': contact.get('engagement_level'),
                        'last_contacted': contact.get('last_contacted_date')
                    },
                    risk_score=self._calculate_contact_risk(contact)
                )
                nodes.append(contact_node)

            # Create edges for relationships
            for engagement in analytics_data.get('engagements', []):
                edge = Edge(
                    source_id=f"contact_{engagement['contact_id']}",
                    target_id=f"deal_{engagement['deal_id']}",
                    type='engagement',
                    attributes={
                        'type': engagement.get('type'),
                        'date': engagement.get('date'),
                        'outcome': engagement.get('outcome')
                    },
                    strength=self._calculate_engagement_strength(engagement)
                )
                edges.append(edge)

            return nodes, edges
        except Exception as e:
            print(f"Error in generate_graph_from_analytics: {str(e)}")
            return [], []

    async def _generate_analyses(self, context_data: Dict) -> Dict:
        """Generate different types of analysis using the LLM."""
        analyses = {}

        for template in [
            PromptTemplate.RISK_ANALYSIS,
            PromptTemplate.OPPORTUNITY_ANALYSIS,
            PromptTemplate.RECOMMENDATIONS
        ]:
            try:
                response = await self.llm_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {
                            "role": "system",
                            "content": self.prompt_manager.get_prompt(PromptTemplate.SYSTEM, **context_data)
                        },
                        {
                            "role": "user",
                            "content": self.prompt_manager.get_prompt(template, **context_data)
                        }
                    ],
                    response_format={"type": "json_object"}
                )

                analyses[template.value] = json.loads(response.choices[0].message.content)
            except Exception as e:
                print(f"Error generating {template.value} analysis: {str(e)}")
                analyses[template.value] = {}

        return analyses

    def _identify_risk_patterns(self, nodes: List[Node], edges: List[Edge]) -> List[Dict]:
        """Identify patterns indicating risk."""
        risk_patterns = []

        try:
            # Identify isolated nodes (contacts/deals with few connections)
            isolated_nodes = self._find_isolated_nodes(nodes, edges)
            if isolated_nodes:
                risk_patterns.append({
                    'type': 'isolation',
                    'description': 'Entities with limited engagement',
                    'affected_nodes': isolated_nodes,
                    'severity': 'high' if len(isolated_nodes) > 3 else 'medium'
                })

            # Identify stagnant deals
            stagnant_deals = [
                node for node in nodes
                if node.type == 'deal' and
                   node.attributes.get('days_in_stage', 0) > 30
            ]
            if stagnant_deals:
                risk_patterns.append({
                    'type': 'stagnation',
                    'description': 'Deals showing no progress',
                    'affected_nodes': [deal.id for deal in stagnant_deals],
                    'severity': 'high' if len(stagnant_deals) > 2 else 'medium'
                })

            # Identify declining engagement
            declining_engagement = self._identify_declining_engagement(nodes, edges)
            if declining_engagement:
                risk_patterns.append(declining_engagement)

            return risk_patterns
        except Exception as e:
            print(f"Error in identify_risk_patterns: {str(e)}")
            return []

    def _identify_opportunity_patterns(self, nodes: List[Node], edges: List[Edge]) -> List[Dict]:
        """Identify patterns indicating opportunities."""
        opportunity_patterns = []

        try:
            # Identify highly engaged contacts
            engaged_contacts = [
                node for node in nodes
                if node.type == 'contact' and
                   node.attributes.get('engagement_level', 0) > 0.7
            ]
            if engaged_contacts:
                opportunity_patterns.append({
                    'type': 'high_engagement',
                    'description': 'Contacts showing strong engagement',
                    'affected_nodes': [contact.id for contact in engaged_contacts],
                    'potential_impact': 'high'
                })

            # Identify potential cross-sell opportunities
            cross_sell_opportunities = self._find_cross_sell_opportunities(nodes, edges)
            if cross_sell_opportunities:
                opportunity_patterns.append({
                    'type': 'cross_sell',
                    'description': 'Potential for additional business',
                    'opportunities': cross_sell_opportunities,
                    'potential_impact': 'medium'
                })

            return opportunity_patterns
        except Exception as e:
            print(f"Error in identify_opportunity_patterns: {str(e)}")
            return []

    def _find_isolated_nodes(self, nodes: List[Node], edges: List[Edge]) -> List[str]:
        """Find nodes with few or no connections."""
        connection_count = {node.id: 0 for node in nodes}

        for edge in edges:
            connection_count[edge.source_id] += 1
            connection_count[edge.target_id] += 1

        return [
            node_id
            for node_id, count in connection_count.items()
            if count < 2  # Consider nodes with less than 2 connections as isolated
        ]

    def _find_cross_sell_opportunities(self, nodes: List[Node], edges: List[Edge]) -> List[Dict]:
        """Identify potential cross-sell opportunities."""
        opportunities = []

        # Find highly engaged contacts not connected to all products/services
        engaged_contacts = [
            node for node in nodes
            if node.type == 'contact' and
               node.attributes.get('engagement_level', 0) > 0.7
        ]

        for contact in engaged_contacts:
            # Find deals/products this contact is connected to
            connected_deals = set()
            for edge in edges:
                if edge.source_id == contact.id:
                    connected_deals.add(edge.target_id)

            # If contact is not connected to all potential products
            if len(connected_deals) < 3:  # Assuming there are multiple product possibilities
                opportunities.append({
                    'contact_id': contact.id,
                    'current_deals': list(connected_deals),
                    'engagement_level': contact.attributes.get('engagement_level'),
                    'potential': 'high' if contact.attributes.get('role') in ['decision_maker',
                                                                              'executive'] else 'medium'
                })

        return opportunities

    def _identify_declining_engagement(self, nodes: List[Node], edges: List[Edge]) -> Optional[Dict]:
        """Identify patterns of declining engagement."""
        try:
            recent_edges = [
                edge for edge in edges
                if (datetime.now() - edge.attributes.get('date', datetime.now())).days <= 30
            ]

            if not recent_edges:
                return {
                    'type': 'declining_engagement',
                    'description': 'No recent engagement activities',
                    'severity': 'high',
                    'affected_nodes': [node.id for node in nodes if node.type == 'contact']
                }

            return None
        except Exception as e:
            print(f"Error in identify_declining_engagement: {str(e)}")
            return None

    def _calculate_graph_metrics(self, nodes: List[Node], edges: List[Edge]) -> Dict:
        """Calculate key metrics from the graph structure."""
        try:
            return {
                'total_nodes': len(nodes),
                'total_edges': len(edges),
                'average_connections': len(edges) / len(nodes) if nodes else 0,
                'risk_distribution': self._calculate_risk_distribution(nodes),
                'node_types': self._count_node_types(nodes),
                'edge_types': self._count_edge_types(edges)
            }
        except Exception as e:
            print(f"Error in calculate_graph_metrics: {str(e)}")
            return {}

    def _calculate_risk_distribution(self, nodes: List[Node]) -> Dict:
        """Calculate distribution of risk scores across nodes."""
        risk_levels = {
            'low': 0,
            'medium': 0,
            'high': 0
        }

        for node in nodes:
            if node.risk_score < 0.3:
                risk_levels['low'] += 1
            elif node.risk_score < 0.7:
                risk_levels['medium'] += 1
            else:
                risk_levels['high'] += 1

        return risk_levels

    def _count_node_types(self, nodes: List[Node]) -> Dict:
        """Count the frequency of each node type."""
        type_counts = {}
        for node in nodes:
            type_counts[node.type] = type_counts.get(node.type, 0) + 1
        return type_counts

    def _count_edge_types(self, edges: List[Edge]) -> Dict:
        """Count the frequency of each edge type."""
        type_counts = {}
        for edge in edges:
            type_counts[edge.type] = type_counts.get(edge.type, 0) + 1
        return type_counts

    def _calculate_deal_risk(self, deal: Dict) -> float:
        """Calculate risk score for a deal."""
        risk_score = 0.0

        try:
            # Consider days in stage
            days_in_stage = deal.get('days_in_stage', 0)
            if days_in_stage > 60:
                risk_score += 0.4
            elif days_in_stage > 30:
                risk_score += 0.2

            # Consider last activity
            last_activity = deal.get('last_activity_date')
            if last_activity:
                days_since_activity = (datetime.now() - last_activity).days
                if days_since_activity > 30:
                    risk_score += 0.3
                elif days_since_activity > 15:
                    risk_score += 0.1

            # Consider deal size and stage
            amount = float(deal.get('amount', 0))
            if amount > 100000:  # High-value deal
                risk_score *= 1.2

            return min(1.0, risk_score)
        except Exception as e:
            print(f"Error in calculate_deal_risk: {str(e)}")
            return 0.5  # Default medium risk

    def _calculate_contact_risk(self, contact: Dict) -> float:
        """Calculate risk score for a contact."""
        risk_score = 0.0

        try:
            # Consider engagement level
            engagement_level = contact.get('engagement_level', 0)
            if engagement_level < 0.3:
                risk_score += 0.4
            elif engagement_level < 0.5:
                risk_score += 0.2

            # Consider role/influence
            if contact.get('role') in ['decision_maker', 'executive']:
                risk_score *= 1.5

            # Consider contact history
            last_contacted = contact.get('last_contacted_date')
            if last_contacted:
                days_since_contact = (datetime.now() - last_contacted).days
                if days_since_contact > 30:
                    risk_score += 0.3

            return min(1.0, risk_score)
        except Exception as e:
            print(f"Error in calculate_contact_risk: {str(e)}")
            return 0.5  # Default medium risk

    def _calculate_engagement_strength(self, engagement: Dict) -> float:
        """Calculate strength of an engagement connection."""
        base_strength = 1.0

        # Adjust based on recency
        days_ago = (datetime.now() - engagement.get('date')).days
        recency_factor = max(0.1, 1 - (days_ago / 30))

        # Adjust based on engagement type
        type_multipliers = {
            'meeting': 1.5,
            'call': 1.2,
            'email': 1.0
        }
        type_multiplier = type_multipliers.get(engagement.get('type'), 1.0)

        return base_strength * recency_factor * type_multiplier

    def _validate_recommendation(self, recommendation: Dict) -> bool:
        """Validate recommendation structure and content."""
        required_fields = ['priority', 'category', 'action', 'expected_outcome', 'timeline']
        return all(field in recommendation for field in required_fields)

    def _generate_implementation_steps(self, recommendation: Dict) -> List[str]:
        """Generate specific implementation steps for a recommendation."""
        base_steps = {
            'engagement': [
                'Review current engagement pattern',
                'Identify key stakeholders',
                'Schedule follow-up activities',
                'Set engagement goals'
            ],
            'pipeline': [
                'Analyze pipeline metrics',
                'Identify bottlenecks',
                'Create action plan',
                'Set milestone dates'
            ],
            'relationship': [
                'Map key relationships',
                'Identify gaps',
                'Plan relationship building activities',
                'Set relationship goals'
            ]
        }

        return base_steps.get(recommendation['category'], [])
