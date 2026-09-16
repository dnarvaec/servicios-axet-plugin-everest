package serenityrest.runner;

import org.junit.platform.suite.api.ConfigurationParameter;
import org.junit.platform.suite.api.IncludeEngines;
import org.junit.platform.suite.api.SelectClasspathResource;
import org.junit.platform.suite.api.Suite;

@Suite
@IncludeEngines("cucumber")
@SelectClasspathResource("features/oficinas/oficinas-avv.feature")
@SelectClasspathResource("features/oficinas/oficinas-bdb.feature")
@ConfigurationParameter(key = "cucumber.glue",        value = "serenityrest.stepdefinitions")
@ConfigurationParameter(key = "cucumber.filter.tags", value = "not @ignore")
@ConfigurationParameter(key = "cucumber.plugin",      value = "io.cucumber.core.plugin.SerenityReporterParallel")
public class CucumberRunnerTest {}