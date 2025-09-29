<!-----



Conversion time: 0.821 seconds.


Using this Markdown file:

1. Paste this output into your source file.
2. See the notes and action items below regarding this conversion run.
3. Check the rendered output (headings, lists, code blocks, tables) for proper
   formatting and use a linkchecker before you publish this page.

Conversion notes:

* Docs to Markdown version 1.0β44
* Mon Sep 29 2025 12:01:53 GMT-0700 (PDT)
* Source doc: Technical direction
* Tables are currently converted to HTML tables.
----->


**Technical direction: Unified AI risk quantification & prevention engine “from incidents to confidence”**

**Big picture**: Capitalism’s answer to novel risks is insurance, standards and audits. Together, they form the confidence infrastructure to let companies adopt.

**Technical direction**: Map incidents -> preventive measures -> evals/red-teaming -> communicating results to create confidence & price insurance.


<table>
  <tr>
   <td><strong>Conceptual flow from incidents to confidence</strong>
   </td>
   <td><strong>Description</strong>
   </td>
   <td><strong>Example</strong>
   </td>
  </tr>
  <tr>
   <td>
<ol>

<li><strong>Incidents</strong>
Ground everything in ground truth.</li>
</ol>
   </td>
   <td>World’s largest up-to-date AI incident database from nation-state attacks down to twitter screenshots of AI creating brand dashers. Focus specifically on incidents that hold up AI adoption.
<p>
Create base rate frequency & severity for each risk.
   </td>
   <td>Hallucinated refund policy @ AirCanada
<ul>

<li>Modality: Text</li>

<li>Harm: Financial loss, Brand Cost: $5,000 + defense cost + brand cost</li>

<li>Frequency: High</li>

<li>Use case: Customer support</li>

<li>Context: Retail, airlines

<p>
Base rate frequency: medium-high
<p>
Base rate severity: medium-low</li>
</ul>
   </td>
  </tr>
  <tr>
   <td>
<ol>

<li><strong>Prevention</strong>
Set the standard for how to prevent real-world incidents.</li>
</ol>
   </td>
   <td>AIUC-1 standard specifies technical, operational and legal controls to deal with each incident.
<p>
New types of incidents -> update standard
<p>
If no safeguards exist -> build it
   </td>
   <td>
<ul>

<li>A001. Testing for hallucination</li>

<li>A002. Groundedness filter</li>

<li>Evidence:</li> 
<ul>
 
<li>A > Vendors X, Y, Z</li>
 
<li>B > Vendors X, Y, Z</li>
 
<li>C > No vendors exist - add to our roadmap</li> 
</ul>

<li>A003. Legal remedies</li>

<li>A004. Incident response plan
> No good monitoring exists so let’s build that</li>
</ul>
   </td>
  </tr>
  <tr>
   <td>
<ol>

<li><strong>Quantification</strong>
Red-team to quantify effectiveness of safeguards & price insurance.</li>
</ol>
   </td>
   <td>Design red-teaming evals for each type of incident to test whether safeguards are effective. 
<p>
Use that to update base rates for frequency & severity estimates for a particular product. This informs insurance premium.
   </td>
   <td>
<ul>

<li>Use case: Customer support</li>

<li>Context: Retail</li>

<li>Modality: text & voice</li>

<li>Tactics: </li> 
<ul>
 
<li>Text: </li>  
<ul>
  
<li>Emotional manipulation</li>
  
<li>Jailbreaks</li>
  
<li>Encoding attacks</li>
  
<li>Role play</li>
  
<li>…</li>  
</ul>
 
<li>Voice:</li>  
<ul>
  
<li>Pitch modification</li>
  
<li>Background noise</li>
  
<li>…
Results: </li>  
</ul></li>  
</ul>

<li>P0: 0</li>

<li>P1: 2</li>

<li>P2: 4</li>

<li>P3: 18</li>

<li>P4: 250</li>
</ul>
   </td>
  </tr>
  <tr>
   <td>
<ol>

<li><strong>Communication</strong>
Visualize safeguards, tests and results to AI buyers to give them confidence to adopt faster.</li>
</ol>
   </td>
   <td>Create dashboards that draw a straight line from (1) real-world incidents they should worry about, (2) safeguards in place, (3) comprehensive third-party tests done, to (4) residual risks they might take on.
   </td>
   <td>[To be drawn]
   </td>
  </tr>
</table>

