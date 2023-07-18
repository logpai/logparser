import random

from ..chromosome.chromosome import Chromosome
from ..chromosome.template import Template
from ..operators.mutation import ChromosomeMutator
from ..utility.chromosome_corrections import fix_all_star_template
from ..utility.match_utility import compute_matched_lines, remove_sub_templates, remove_super_templates


class ChromosomeMutator100cov(ChromosomeMutator):

    def apply_mutation(self, ch: Chromosome):
        """ Applies mutation on a chromosome
        modify an existing template from a cluster
        :param ch: chromosome to mutate
        :return: the modified chromosome
        """

        cluster_id = random.choice(list(ch.templates.keys()))
        prob = 1.0 / ch.cluster_size(cluster_id)

        for template_index in range(0, ch.cluster_size(cluster_id)):
            if random.random() <= prob:
                self.change_template(ch, cluster_id, template_index)
                # Once the chromosome is changed,
                # we have to update the matched lines (only for the unchanged templates)
                fix_all_star_template(ch, cluster_id, template_index, self.chGenerator.messages)
                compute_matched_lines(self.chGenerator.messages, ch.templates[cluster_id][template_index])

        # add templates to reach 100% coverage if not satisfied for the modified cluster
        #if random.random() <= 0.50:
        remove_sub_templates(ch, cluster_id)
        #else:
        #    remove_super_templates(ch, cluster_id)
        self.add_template_to_reach_100cov(ch, cluster_id)

    def add_template_to_reach_100cov(self, ch: Chromosome, cluster_id: int):
        uncovered_lines = set(range(len(self.chGenerator.messages[cluster_id])))
        for template in ch.templates[cluster_id]:
            uncovered_lines = uncovered_lines.difference(template.matched_lines)
        while len(uncovered_lines) > 0:
            message_index = random.choice(list(uncovered_lines))
            template = self.chGenerator.generate_template_from_line(cluster_id, message_index)
            ch.add_template(template)
            compute_matched_lines(self.chGenerator.messages, template)
            uncovered_lines = uncovered_lines.difference(template.matched_lines)
