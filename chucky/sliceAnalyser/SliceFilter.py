from settings import Defaults

from joernInterface.JoernInterface import jutils
from joernInterface.nodes.ASTNode import ASTNode
from joernInterface.indexLookup.ParameterLookup import ParameterLookup
from joernInterface.indexLookup.IdentifierDeclLookup import IdentifierDeclLookup
from joernInterface.indexLookup.CallExpressionLookup import CallExpressionLookup

from collections import defaultdict as dict

import logging

SOURCE = Defaults.SOURCE
SINK = Defaults.SINK
NOS = 'nosink_or_nosource'

class SliceFilter(object):
   
    def __init__(self, job):
        self.job = job
        self.logger = logging.getLogger('chucky')

    def filter(self, systems):
        if self.job.category == SOURCE:
            accept = self._select_accepted_sinks()
            self.logger.debug("Filter by sink(s) ({})".format(', '.join(accept)))
            return self.filter_by_source_sinks('statementToSinks',accept,systems)
        else:
            accept = self._select_accepted_sources()
            self.logger.debug("Filter by source(s) ({})".format(', '.join(accept)))
            return self.filter_by_source_sinks('statementToSources',accept,systems)
        
        
        
    
    def filter_by_source_sinks(self,step,accept,systems):       
        common_ss = dict(set)
        other_ss = dict(set)

        for statement, symbol in systems:
            source_or_sinks = self._select(step, statement, symbol)
            for s in source_or_sinks:
                if s in accept:
                    common_ss[s].add((statement, symbol))
                else:
                    other_ss[s].add((statement, symbol))
            if not source_or_sinks:
                if not accept:
                    common_ss[NOS].add((statement, symbol))
                else:
                    other_ss[NOS].add((statement, symbol))
        try:
            result = set()
            for s in sorted(common_ss, key = lambda x : len(common_ss[x]), reverse = True):
                if len(result) >= self.job.n_neighbors:
                    break;
                else:
                    self.logger.debug('+ Selected {} {}, {} matching slices.'.format(self.job.category,s, len(common_ss[s])))
                    result.update(common_ss[s])
            #for sink in sorted(other_ss, key = lambda x : len(other_ss[x]), reverse = True):
            #    if len(result) >= self.job.n_neighbors:
            #        break;
            #    else:
            #        self.logger.debug('- Selected sink {}, {} matching slices.'.format(sink, len(other_ss[sink])))
            #        result.update(other_ss[sink])
        except Exception, e:
            self.logger.error(e)
            return []
        else:
            if len(result) >= self.job.n_neighbors:
                return list(result)
            elif len(result) > 1:
                return list(result)
            else:
                return []

    def _select_accepted_sinks(self):
        node_selection = self.job.target.node_selection
        if self.job.symbol_type == 'CallExpression':
            symbol = self.job.symbol.return_symbol()
        else:
            symbol = self.job.symbol_name
        return self._select('statementToSinks',self.job.target, symbol)

    def _select_accepted_sources(self):
        node_selection = self.job.target.node_selection
        if self.job.symbol_type == 'CallExpression':
            symbols = self.job.symbol.arguments()
            result=set()
            for symbol in symbols:
                sources=self._select('statementToSources',self.job.target, symbol)
                result.update(sources)
            return result
        else:
            symbol = self.job.symbol_name
            return self._select('statementToSources',self.job.target, symbol)
    
    def _select(self, step_name, statement, symbol):
        traversal = "{}('{}')".format(step_name,symbol)
        command = '.'.join([statement.node_selection, traversal])
        source_or_sinks = jutils.runGremlinCommands([command])
        return source_or_sinks    